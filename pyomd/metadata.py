"""Metadata-related objects."""

from __future__ import annotations

import datetime
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Callable, Optional, Tuple, Type, Union

import frontmatter  # type: ignore

from pyomd.config import CONFIG

from .exceptions import ArgTypeError, InvalidFrontmatterError
from .misc import Order

if TYPE_CHECKING:
    from note import Note

UserInput = Union[str, int, float]
MetaValues = Union[list[str], None]
MetaDict = dict[str, MetaValues]
ParseFunction = Callable[[str], tuple[MetaDict, str]]
Number = Union[int, float]
Span = tuple[int, int]
SpanList = list[Span]


class MetadataType(Enum):
    """Type of metadata.

    Possible values:
        FRONTMATTER: note frontmatter
        INLINE: inline metadata (dataview style)
        ALL: note metadata, wherever it is located (inline, or frontmatter)
        DEFAULT: default location where to define new metadata
    """

    FRONTMATTER = "frontmatter"
    INLINE = "inline"
    ALL = "notemeta"
    DEFAULT = "default"

    @staticmethod
    def get_from_str(s: Union[str, None]) -> MetadataType:
        """Returns Enum value from string.

        Args:
            s:
                string value.
        """
        if s is None:
            return MetadataType.ALL
        for k in MetadataType:
            if s == k.value:
                return k
        raise ValueError(f'Metadatatype not defined: "{s}"')


class Metadata(ABC):
    """Common attributes and methods for all types of metadata."""

    def __init__(self, note_content: str):
        self.metadata: MetaDict = self._parse(note_content)

    def __repr__(self):
        rpr = f"{type(self)}:\n"
        if self.to_string() is None:
            rpr += " None"
        else:
            rpr += "".join(
                [f'- {k}: {", ".join(v)}\n' for k, v in self.metadata.items()]
            )
        return rpr

    @abstractmethod
    def to_string(self) -> str:
        ...

    def get(self, k: str) -> Union[list[str], None]:
        """Gets metadata field.

        Args:
            k:
                metadata key
        Returns:
            Values of the metadata field. Returns None if k is not in the metadata keys
        """
        return self.metadata.get(k, None)

    def has(self, k: str, l: Union[list[str], None, str] = None) -> bool:
        """Checks if metadata contains field k and values l.

        Args:
            k:
                metadata key.
            l:
                values of the metadata field. If set to None, no values are checked.
                To check if metadata[k] is empty, set l to an empty list.
        Returns:
            Boolean
        """
        b_has = k in self.metadata
        if l is None:
            return b_has
        if isinstance(l, str):
            l = [l]
        if b_has and len(l) == 0:
            b_has = self.metadata[k] == []
        if b_has and len(l) > 0:
            b_has = all(val in self.metadata[k] for val in l)
        return b_has

    def add(
        self,
        k: str,
        l: Union[UserInput, list[UserInput], None],
        overwrite: bool = False,
        allow_duplicates: bool = False,
    ) -> None:
        """Adds a metadata key and/or new values.

        Args:
            k:
                metadata key
            l:
                metadata values
            overwrite:
                Overwrite the existing values or not.
            allow_duplicates:
                Allow for duplicate values for a given metadata key.
        """
        if l is None:
            nl = list()
        elif isinstance(l, UserInput):
            nl = [str(l)]
        else:
            nl = [str(x) for x in l]

        if overwrite:
            self.metadata[k] = nl
        else:
            if k in self.metadata:
                if allow_duplicates:
                    self.metadata[k] += nl
                else:
                    self.metadata[k] += [x for x in nl if x not in self.metadata[k]]
            else:
                self.metadata[k] = nl

    def remove(
        self, k: str, l: Optional[Union[UserInput, list[UserInput]]] = None
    ) -> None:
        """Removes a metadata key or particular values.

        See `NoteMetadata.remove` for argument description
        """
        if k not in self.metadata:
            return
        if l is None:
            del self.metadata[k]
            return
        nl = [str(l)] if isinstance(l, UserInput) else [str(x) for x in l]
        self.metadata[k] = [e for e in self.metadata[k] if e not in nl]

    def remove_empty(self) -> None:
        """removes empty metadata fields.

        See `NoteMetadata.remove_rempty` for argument description
        """
        empty: list[str] = list()
        for k in self.metadata:
            if len(self.metadata[k]) == 0:
                empty.append(k)

        for k in empty:
            del self.metadata[k]

    def remove_duplicate_values(self, k: Union[str, list[str], None] = None) -> None:
        """Removes duplicate values of a metadata key.

        See `NoteMetadata.remove_duplicate_values` for argument description
        """

        if k is None:
            list_keys = list(self.metadata.keys())
        elif isinstance(k, str):
            list_keys = [k]
        elif isinstance(k, list):
            list_keys = k
        else:
            raise ArgTypeError(
                var_name="k",
                type_given=type(k),
                type_expected=str(Union[str, list[str], None]),
            )

        for k2 in list_keys:
            if k2 not in self.metadata:
                continue
            self.metadata[k2] = list(dict.fromkeys(self.metadata[k2]))

    def order_values(
        self, k: Union[str, list[str], None] = None, how: Order = Order.ASC
    ) -> None:
        """Orders metadata values.

        See `NoteMetadata.order_values` for argument description
        """
        if not isinstance(how, Order):
            raise ArgTypeError(var_name="how", type_given=type(how), type_expected=Order)  # type: ignore

        if k is None:
            k = list(self.metadata.keys())
        if isinstance(k, str):
            k = [k]
        for e in k:
            reverse = False if (how == Order.ASC) else True
            self.metadata[e] = sorted(self.metadata[e], reverse=reverse)

    def order_keys(self, how: Order = Order.ASC) -> None:
        """Orders metadata keys.

        Uses the property that for python>=3.6, python dict remember insert order.

        See `NoteMetadata.order_keys` for argument description
        """
        reverse = how == Order.DESC
        list_keys = sorted(list(self.metadata.keys()), reverse=reverse)
        self.metadata = {k: self.metadata.pop(k) for k in list_keys}

    def order(
        self,
        k: Union[str, list[str], None] = None,
        o_keys: Union[Order, None] = Order.ASC,
        o_values: Union[Order, None] = Order.ASC,
    ):
        """Orders metadata keys and values.

        See `NoteMetadata.order` for argument description
        """
        if o_keys is not None:
            self.order_keys(how=o_keys)
        if o_values is not None:
            self.order_values(k=k, how=o_values)
        return None

    def print(self):
        """Prints metadata information."""
        print(self.to_string())

    @abstractmethod
    def _update_content(self, note_content: str) -> str:
        ...

    @classmethod
    @abstractmethod
    def _parse(
        cls, note_content: str, parse_fn: Union[ParseFunction, None] = None
    ) -> MetaDict:
        pass

    @staticmethod
    def _parse_special_fields(metadata: MetaDict, meta_type: MetadataType) -> MetaDict:
        """Parse special fields."""
        sep_field_name = f"{meta_type.value}_separators"
        for k in metadata:
            b1 = k in CONFIG.cfg["fields"]
            b2 = sep_field_name in CONFIG.cfg["fields"].get(k, {})
            if b1 and b2:
                for sep in CONFIG.cfg["fields"][k][sep_field_name]:
                    tmp = sep.join(metadata[k])
                    metadata[k] = [t.strip() for t in tmp.split(sep) if t.strip() != ""]
        return metadata

    @classmethod
    @abstractmethod
    def _erase(cls, note_content: str) -> str:
        pass

    @classmethod
    def _exists(cls, note_content: str) -> bool:
        """Checks if the metadata type is present in the note"""
        try:
            meta_dict = cls._parse(note_content)
        except Exception as _:
            meta_dict = {}
        return len(meta_dict) > 0


class Frontmatter(Metadata):
    """A note's frontmatter.

    Attributes:
        self.metadata MetaDict:
            metadata dictionary
    """

    REGEX = "(?s)(^---\n).*?(\n---\n)"

    def _quotifyLink(self, value) -> str:
        """ Add quotes around Obsidian internal links found in metadata
            property values

            Returns:
                String: value in double quotes if value is an internal link; otherwise,
                the original value
        """
        if value.startswith("[[") and value.endswith("]]"):
            return f"\"{value}\""
        else:
            return value


    def to_string(self) -> str:
        """Render metadata as a string.

        Returns:
            String representation of the metadata
        """
        if len(self.metadata) == 0:
            return ""
        metadata_repr = ""
        for k, v in self.metadata.items():
            if len(v) == 1:
                metadata_repr += f"{k}: {self._quotifyLink(v[0])}\n"
            elif len(v) == 0:
                metadata_repr += f"{k}: \n"
            else:
                metadata_repr += f'{k}: ['
                for v1 in v:
                    metadata_repr += f'{self._quotifyLink(v1)}'
                    metadata_repr += "]\n" if v1 is v[-1] else ', '
        out = "---\n" + metadata_repr + "---\n"
        return out

    def _update_content(self, note_content: str) -> str:
        """Returns the note content with the updated metadata.

        Args:
            note_content:
                The note content
        """
        content_no_meta = self._erase(note_content)
        res = self.to_string() + content_no_meta
        return res

    @staticmethod
    def is_frontmatter_valid(path: Path) -> bool:
        """Checks if the file frontmatter is valid."""
        try:
            with open(path, "r") as f:
                frontmatter.load(f)  # type: ignore
        except:
            return False
        return True

    @classmethod
    def _parse(
        cls, note_content: str, parse_fn: Union[ParseFunction, None] = None
    ) -> MetaDict:
        """Parse note content to extract metadata dictionary."""
        if parse_fn is None:
            parse_fn = cls._parse_1
        return parse_fn(note_content)

    @classmethod
    def _parse_1(cls, note_content: str) -> MetaDict:
        """Parse note content to extract metadata dictionary.
        Uses the python-frontmatter library."""
        try:
            fm = frontmatter.loads(note_content)
        except Exception as e:
            raise InvalidFrontmatterError(exception=e) from e

        meta_dict: MetaDict = fm.metadata

        for k in meta_dict:
            if meta_dict[k] is None:
                meta_dict[k] = list()

        # make all elements into list of strings
        for k, v in meta_dict.items():
            # print(f'K = "{k}"\nV = "{v}"\ntype(V) = "{type(v)}"')
            if isinstance(v, str):
                meta_dict[k] = [v]
            elif isinstance(v, list):
                meta_dict[k] = [str(x) for x in v]
            elif isinstance(v, Number):
                meta_dict[k] = [str(v)]
            elif isinstance(v, datetime.date):
                meta_dict[k] = [str(v)]

        meta_dict = cls._parse_special_fields(
            metadata=meta_dict, meta_type=MetadataType.FRONTMATTER
        )
        return meta_dict

    @classmethod
    def _parse_2(cls, note_content: str) -> MetaDict:
        """Parse frontmatter metadata using regex"""
        mtc = re.search(cls.REGEX, note_content)
        if mtc is None:
            ext_str = list()
        fm_str = mtc.group()
        ext_str = [fm_str]

        # convert extracted string to dictionary
        metadata: MetaDict = {}
        if len(ext_str) == 0:
            return {}
        ms = ext_str[0]
        elements = ms.split("\n")
        for e in elements:
            if ":" not in e:
                continue
            k, v = e.split(":", maxsplit=1)
            c = [v.strip()] if "," not in v else [x.strip() for x in v.split(",")]
            metadata[k.strip()] = c
        if "tags" in metadata:
            mtags = " ".join(metadata["tags"])
            metadata["tags"] = [t.strip() for t in mtags.split(" ") if t.strip() != ""]

        return metadata

    @classmethod
    def _erase(cls, note_content: str) -> str:
        r: str = frontmatter.loads(note_content).content
        return r


class InlineMetadata(Metadata):
    """A note's inline metadata (dataview style).

    Attributes:
        self.metadata MetaDict:
            metadata dictionary
    """

    TMP_REGEX = Template(r"(?P<beg>.*?)(?P<key>$key)::(?P<values>.*)")
    TMP_REGEX_ENCLOSED = Template(
        r"(?P<beg>.*?)(?P<open>[(\[])(?P<key>$key)::(?P<values>.*?)(?P<close>[)\]])(?P<end>.*)"
    )
    REGEX = re.compile(TMP_REGEX.substitute(key="[A-z][A-z0-9_ -]*"))
    REGEX_ENCLOSED = re.compile(TMP_REGEX_ENCLOSED.substitute(key=".*?"))

    def to_string(
        self,
        ignore_k: Union[str, list[str], None] = None,
        tml: Union[str, Callable] = "standard",
    ) -> str:
        """Render metadata as a string.

        Args:
            ignore_k:
                metadata keys to ignore.
            tml:
                Template function to use to display inline metadata.

        Returns:
            String representation of the metadata
        """
        if tml == "standard":
            tml = self._tml_standard
        elif tml == "callout":
            tml = self._tml_callout

        if ignore_k is None:
            ignore_k = list()
        if isinstance(ignore_k, str):
            ignore_k = [ignore_k]
        meta_dict = {k: v for (k, v) in self.metadata.items() if k not in ignore_k}
        if len(meta_dict) == 0:
            return ""
        out = tml(meta_dict)
        return out

    def _update_content(
        self,
        note_content: str,
        position: str = "bottom",
        inplace: bool = True,
        tml: Union[str, Callable] = "standard",  # type: ignore
    ) -> str:
        """
        position:
            - bottom
            - top
        inplace:
            - replace inline metadata inplace (for existing fields in the note)
        """
        if inplace:
            nc, ignore_k = self._update_content_inplace(note_content=note_content)
        else:
            nc, ignore_k = self._erase(note_content), None
        sep = self._get_sep_newlines(nc, position=position)
        if position == "top":
            new_nc = self.to_string(ignore_k=ignore_k, tml=tml) + sep + nc
        elif position == "bottom":
            new_nc = nc + sep + self.to_string(ignore_k=ignore_k, tml=tml)
        else:
            raise NotImplementedError
        new_nc = new_nc.strip()
        return new_nc

    @classmethod
    def _parse(
        cls, note_content: str, parse_fn: Union[ParseFunction, None] = None
    ) -> MetaDict:
        """Parse note content to extract metadata dictionary."""
        if parse_fn is None:
            parse_fn = cls._parse_1
        return parse_fn(note_content)

    @classmethod
    def _parse_1(cls, note_content: str) -> MetaDict:
        """Parse note content to extract metadata dictionary.

        Uses the python-frontmatter library.
        """

        matches: list[re.Match] = list()
        for l in note_content.split("\n"):
            m = cls.REGEX.search(l)
            b = m is not None
            b_enc = cls.REGEX_ENCLOSED.search(l) is not None
            if b and not b_enc:
                matches.append(m)

        tmp: dict[str, list[str]] = dict()
        for m in matches:
            k = m.group("key").strip()
            v = m.group("values")
            tmp[k] = tmp.get(k, "") + ", " + v
        metadata: MetaDict = {
            k: [x.strip() for x in v.split(",") if len(x.strip()) > 0]
            for (k, v) in tmp.items()
        }

        metadata = cls._parse_special_fields(
            metadata=metadata, meta_type=MetadataType.INLINE
        )
        return metadata

    @classmethod
    def _erase(cls, note_content: str) -> str:

        keep: list[str] = list()
        for l in note_content.split("\n"):
            b_match = re.search(cls.REGEX, l) is not None
            b_match_enclosed = re.search(cls.REGEX_ENCLOSED, l) is not None
            if b_match and not b_match_enclosed:
                continue
            keep.append(l)
        content_no_meta = "\n".join(keep)

        ## artefacts to erase
        artefacts = [re.escape("> [!info]- metadata") + "(\n\n|$)"]
        for a in artefacts:
            content_no_meta = re.sub(a, "", content_no_meta)
        return content_no_meta

    @staticmethod
    def _get_sep_newlines(content_no_meta: str, position: str = "bottom") -> str:
        if position == "top":
            if len(content_no_meta) >= 1 and content_no_meta[0] != "\n":
                sep = "\n\n"
            elif len(content_no_meta) >= 1 and content_no_meta[0:2] != "\n\n":
                sep = "\n"
            else:
                sep = ""
        elif position == "bottom":
            if len(content_no_meta) >= 1 and content_no_meta[-1] != "\n":
                sep = "\n\n"
            elif len(content_no_meta) >= 2 and content_no_meta[-2:] != "\n\n":
                sep = "\n"
            else:
                sep = ""
        else:
            sep = ""
        return sep

    @staticmethod
    def _get_spans_to_delete(
        s: str,
        r: re.Pattern,
        r_enc: re.Pattern,
        meta_dict: dict,
        debug: bool = False,
    ) -> SpanList:
        sp_del: SpanList = list()
        for m in r.finditer(s):
            if r_enc.match(m.group()):
                continue
            k = m.group(2).strip()
            if k not in meta_dict:
                sp_del.append(m.span())
        return sp_del

    @staticmethod
    def _delete_span(s: str, span: Span) -> str:
        s = s[: span[0]] + s[span[1] :]
        return s

    @staticmethod
    def _delete_spans(s: str, spans: SpanList):
        offset = 0
        for span in spans:
            p1, p2 = span
            span_offset = (p1 - offset, p2 - offset)
            s = InlineMetadata._delete_span(s, span_offset)
            len_span = p2 - p1
            offset += len_span
        return s

    @staticmethod
    def _get_span_redundant_keys(
        s: str, r: re.Pattern, r_enc: re.Pattern, debug: bool = False
    ) -> SpanList:
        """Returns spans for inline metadata which keys appear earlier in the file content."""
        found_keys: set[str] = set()
        spans_del: SpanList = list()
        for m in r.finditer(s):
            if r_enc.match(m.group()):
                continue
            k = m.group(2).strip()
            if debug:
                print(f'"{k}"')
            if k in found_keys:
                spans_del.append(m.span())
                if debug:
                    print(f'to delete: "{m.group()}"')
            else:
                found_keys.add(k)
                if debug:
                    print(f"keep: {m.group()}")
        return spans_del

    def _update_content_inplace(self, note_content: str) -> Tuple[str, set[str]]:
        """
        Updates inline metadata in place.

        Returns a tuple:
            - updated note_content
            - list of updated fields.
        """

        rgx = re.compile(self.REGEX.pattern + "\n?")

        # remove fields that aren't in the metadata dictionary anymore
        spans: SpanList = self._get_spans_to_delete(
            s=note_content, r=rgx, r_enc=self.REGEX_ENCLOSED, meta_dict=self.metadata
        )
        note_content = self._delete_spans(note_content, spans)

        # remove redundant inline metadata
        spans_redundant = self._get_span_redundant_keys(
            s=note_content, r=rgx, r_enc=self.REGEX_ENCLOSED
        )
        note_content = self._delete_spans(note_content, spans_redundant)

        # update fields still in metadata dictionary
        updated_fields: set[str] = set()
        for key in self.metadata:
            # print(f'this is key: "{key}"')
            new_v = ", ".join(self.metadata[key])
            regex_field = re.compile(self.TMP_REGEX.substitute(key=f"{key} *"))
            for m in regex_field.finditer(note_content):
                updated_fields.add(key)
                beg = m.group("beg")
                k = m.group("key")
                rep = f"{beg}{k.strip()} :: {new_v}"
                note_content = regex_field.sub(rep, note_content)

        return (note_content, updated_fields)

    @staticmethod
    def _tml_standard(meta_dict: dict = None) -> str:  # type: ignore
        """
        Args:
            - meta_dict: dictionary containing inline metadata (k,v pairs)
        """
        if meta_dict is None:
            meta_dict = {}
        tmp = [f"{k}:: {', '.join(v)}" for k, v in meta_dict.items()]
        out = "\n".join(tmp)
        return out

    @staticmethod
    def _tml_callout(meta_dict: dict = None) -> str:
        """
        Args:
            - meta_dict: dictionary containing inline metadata (k,v pairs)
        """
        if meta_dict is None:
            meta_dict = {}
        tmp = ["> [!info]- metadata"]
        tmp += [f"> {k} :: {', '.join(v)}" for k, v in meta_dict.items()]
        out = "\n".join(tmp)
        return out


class NoteMetadata:
    """API to the note's metadata (frontmatter + inline).

    Attributes:
        frontmatter:
            frontmatter metadata
        inline:
            inline metadata
    """

    def __init__(self, note_content: str):
        self.frontmatter = Frontmatter(note_content)
        self.inline = InlineMetadata(note_content)

    @classmethod
    def _parse_arg_meta_type(cls, meta_type: Union[MetadataType, None]) -> MetadataType:
        if meta_type is None:
            meta_type = MetadataType.ALL
        if not isinstance(meta_type, MetadataType):  # type: ignore
            raise ArgTypeError(
                var_name="meta_type",
                type_given=type(meta_type),
                type_expected=str(Union[MetadataType, None]),
            )
        return meta_type

    def get_default_metadata(self, k: Optional[str]):
        """Get default metadata, as defined in the library configuration parameters.

        Args:
            k:
                Key for which to check the default metadata.
                If None, returns the global default metadata

        """
        b1 = (k is not None) and (k in CONFIG.cfg["fields"])
        b2 = "default_meta" in CONFIG.cfg["fields"].get(k, {})
        if b1 and b2:
            meta_type = MetadataType.get_from_str(
                CONFIG.cfg["fields"][k]["default_meta"]
            )
        else:
            meta_type = MetadataType.get_from_str(CONFIG.cfg["global"]["default_meta"])
        return meta_type

    def get(self, k: str, meta_type: Union[MetadataType, None] = None) -> MetaValues:
        """Returns metadata values for the given key.

        Args:
            k:
                metadata key
            meta_type:
                metadata type to check from. Set to None to check all metadata types

        Returns:
            If meta_type is set to None, returns frontmatter.metadata[k] + inline.metadata[k]
        """
        if meta_type == MetadataType.DEFAULT:
            meta_type = self.get_default_metadata(k)

        get_fm = self.frontmatter.get(k=k)
        get_il = self.inline.get(k=k)
        if meta_type == MetadataType.FRONTMATTER:
            return get_fm
        if meta_type == MetadataType.INLINE:
            return get_il
        if meta_type is None:
            if (get_fm is None) and (get_il is None):
                return None
            if get_fm is None:
                return get_il
            if get_il is None:
                return get_fm
            return get_fm + get_il

    def has(
        self,
        k: str,
        l: Union[list[str], None, str] = None,
        meta_type: Union[MetadataType, None] = None,
    ) -> bool:
        """Checks if metadata contains field k and values l in a given meta type.

        Args:
            k:
                metadata key.
            l:
                values of the metadata field. If set to None, no values are checked.
                To check if metadata[k] is empty, set l to an empty list.
            meta_type:
                metadata type. If None, it returns true if it finds the expected values
                in any of the metadata types.

        Returns:
            Boolean
        """
        b_has_fm = self.frontmatter.has(k=k, l=l)
        b_has_il = self.inline.has(k=k, l=l)
        if meta_type is None:
            return b_has_fm or b_has_il
        if meta_type == MetadataType.FRONTMATTER:
            return b_has_fm
        if meta_type == MetadataType.INLINE:
            return b_has_il
        else:
            raise NotImplementedError

    def add(
        self,
        k: str,
        l: Union[UserInput, list[UserInput], None],
        meta_type: MetadataType = MetadataType.DEFAULT,
        overwrite: bool = False,
        allow_duplicates: bool = False,
    ):
        """Adds a metadata field (k,v)

        Args:
            k:
                metadata key
            l:
                values or list of values for the metadata key
            meta_type:
                The metadata type to add to
            overwrite:
                If precedent values for the metadata key provided should be overwritten.
                If false, new values are appended instead.
            allow_duplicates:
                Allow duplicate values.
        """
        if meta_type == MetadataType.DEFAULT:
            meta_type = self.get_default_metadata(k)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.add(
                k=k, l=l, overwrite=overwrite, allow_duplicates=allow_duplicates
            )
        if meta_type == MetadataType.INLINE:
            self.inline.add(
                k=k, l=l, overwrite=overwrite, allow_duplicates=allow_duplicates
            )

    def remove(
        self,
        k: str,
        l: Optional[Union[UserInput, list[UserInput]]] = None,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Removes a metadata key or particular values.

        Args:
            k:
                metadata key
            l:
                metadata values
            meta_type:
                metadata type to modify.
                If None, removes from both the frontmatter and inline metadata
        """
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.remove(k=k, l=l)
        if meta_type == MetadataType.INLINE:
            self.inline.remove(k=k, l=l)
        if meta_type is None:
            self.frontmatter.remove(k=k, l=l)
            self.inline.remove(k=k, l=l)

    def remove_empty(
        self,
        meta_type: MetadataType = MetadataType.ALL,
    ):
        """removes empty metadata fields.

        Args:
            meta_type:
                metadata type. Defaults to MetadataType.ALL:
                All metadata fields with empty values are removed,
                from the frontmatter and inline.
        """
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.remove_empty()
        if meta_type == MetadataType.INLINE:
            self.inline.remove_empty()
        if meta_type is MetadataType.ALL:
            self.frontmatter.remove_empty()
            self.inline.remove_empty()

    def remove_duplicate_values(
        self,
        k: Union[str, list[str], None] = None,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Remove duplicate values in the note's metadata

        Args:
            k:
                key or list of keys on which to perform the duplication removal. If None, does it on all keys.
            meta_type:
                metadata type. If None, performs the operation on all metadata types.
        """
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.remove_duplicate_values(k=k)
        elif meta_type == MetadataType.INLINE:
            self.inline.remove_duplicate_values(k=k)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.remove_duplicate_values(k=k)
            self.inline.remove_duplicate_values(k=k)
        else:
            raise ValueError(f"Unsupported value for argument meta_type: {meta_type}")

    def order_values(
        self,
        k: Union[str, list[str], None] = None,
        how: Order = Order.ASC,
        meta_type: Union[MetadataType, None] = None,
    ) -> None:
        """Order the values of a metadata field.

        Args:
            k:
                metadata keys to order. If None, order values of all metadata keys
            how:
                "asc" (ascending) or "desc" (descending)
            meta_type:
                IF None, orders on all type of metadata (frontmatter and inline)
        """
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order_values(k=k, how=how)
        elif meta_type == MetadataType.INLINE:
            self.inline.order_values(k=k, how=how)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order_values(k=k, how=how)
            self.inline.order_values(k=k, how=how)
        else:
            raise ValueError(f"Unsupported value for argument meta_type: {meta_type}")

    def order_keys(
        self, how: Order = Order.DESC, meta_type: Union[MetadataType, None] = None
    ) -> None:
        """Order metadata keys.

        Args:
            how:
                "asc" or "desc"
            meta_type:
                If None, orders on all type of metadata (frontmatter and inline)
        """
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order_keys(how=how)
        elif meta_type == MetadataType.INLINE:
            self.inline.order_keys(how=how)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order_keys(how=how)
            self.inline.order_keys(how=how)
        else:
            raise ValueError(f"Unsupported value for argument meta_type: {meta_type}")

    def order(
        self,
        k: Union[str, list[str], None] = None,
        o_keys: Union[Order, None] = Order.ASC,
        o_values: Union[Order, None] = Order.ASC,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Order metadata keys and values.

        Args:
            k:
                key or list of keys to order. If None, order all.
            o_keys:
                How to order keys. "asc" or "desc". If None, don't order them.
            o_values:
                How to order values. "asc" or "desc". If None, don't order them.
            meta_type:
                If None, orders on all type of metadata (frontmatter and inline)
        """
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order(k=k, o_keys=o_keys, o_values=o_values)
        elif meta_type == MetadataType.INLINE:
            self.inline.order(k=k, o_keys=o_keys, o_values=o_values)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order(k=k, o_keys=o_keys, o_values=o_values)
            self.inline.order(k=k, o_keys=o_keys, o_values=o_values)
        else:
            raise ValueError(f"Unsupported value for argument meta_type: {meta_type}")

    def move(
        self,
        k: Union[str, list[str], None] = None,
        fr: Union[MetadataType, None] = None,
        to: Union[MetadataType, None] = None,
    ):
        """Move a metadata field between frontmatter and inline.

        Args:
            k:
                Key of the metadata field to move. If None, move all fields.
            fr:
                metadata type to move from.
            to:
                metadata type to move to.
        """
        if (k is None) and (fr is None) and (to is None):
            for k2 in CONFIG.cfg["fields"]:
                if "default_meta" in CONFIG.cfg["fields"][k2]:
                    default_meta = MetadataType.get_from_str(
                        CONFIG.cfg["fields"][k2]["default_meta"]
                    )
                    m_to = (
                        self.frontmatter
                        if default_meta == MetadataType.FRONTMATTER
                        else self.inline
                    )
                    m_from = (
                        self.frontmatter
                        if default_meta == MetadataType.INLINE
                        else self.inline
                    )
                    if k2 in m_from.metadata:
                        m_to.add(k=k2, l=m_from.metadata[k2])
                        m_from.remove(k=k2)
            return

        assert (fr is not None) and (to is not None), "args 'fr' and 'to' should be set"
        m_from = self.inline if fr == MetadataType.INLINE else self.frontmatter
        m_to = self.inline if to == MetadataType.INLINE else self.frontmatter

        if k is None:
            k = list(m_from.metadata.keys())
        if isinstance(k, str):
            k = [k]
        for k2 in k:
            if k2 in m_from.metadata:
                m_to.add(k=k2, l=m_from.metadata[k2])
                m_from.remove(k=k2)

    def _update_content(
        self,
        note_content: str,
        inline_position: str = "bottom",
        inline_inplace: bool = True,
        inline_tml: Union[str, Callable] = "standard",  # type: ignore
    ) -> str:
        """Update the note's metadata (frontmatter and inline)"""
        str_no_fm = self.frontmatter._erase(note_content)
        res = self.inline._update_content(
            str_no_fm, position=inline_position, inplace=inline_inplace, tml=inline_tml
        )
        res = self.frontmatter.to_string() + res
        return res


class NoteMetadataBatch:
    """API to modify in batch metadata from a Notes object."""

    def __init__(self, notes: list[Note]):
        self.notes = notes

    def add(
        self,
        k: str,
        l: Union[UserInput, list[UserInput], None],
        meta_type: MetadataType = MetadataType.DEFAULT,
        overwrite: bool = False,
        allow_duplicates: bool = False,
    ):
        """Add metadata to the batch of notes.

        See `NoteMetadata.add` for argument description
        """
        for note in self.notes:
            note.metadata.add(
                k=k,
                l=l,
                meta_type=meta_type,
                overwrite=overwrite,
                allow_duplicates=allow_duplicates,
            )

    def remove(
        self,
        k: str,
        l: Optional[Union[UserInput, list[UserInput]]] = None,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Removes metadata from the batch of notes.

        See `NoteMetadata.remove` for argument description
        """
        for note in self.notes:
            note.metadata.remove(k=k, l=l, meta_type=meta_type)

    def move(
        self,
        k: Union[str, list[str], None] = None,
        fr: Union[MetadataType, None] = None,
        to: Union[MetadataType, None] = None,
    ):
        """Moves metadata for the batch of notes.

        See `NoteMetadata.move` for argument description
        """
        for note in self.notes:
            note.metadata.move(k=k, fr=fr, to=to)

    def remove_duplicate_values(
        self,
        k: Union[str, list[str], None] = None,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Remove duplicate metadata values for the batch of notes.

        See `NoteMetadata.remove_duplicate_values` for argument description
        """
        for note in self.notes:
            note.metadata.remove_duplicate_values(k=k, meta_type=meta_type)

    def order(
        self,
        k: Union[str, list[str], None] = None,
        o_keys: Union[Order, None] = Order.ASC,
        o_values: Union[Order, None] = Order.ASC,
        meta_type: Union[MetadataType, None] = None,
    ):
        """Orders metadata for the batch of notes.

        See `NoteMetadata.order` for argument description
        """
        for note in self.notes:
            note.metadata.order(
                k=k, o_keys=o_keys, o_values=o_values, meta_type=meta_type
            )


def return_metaclass(
    meta_type: MetadataType,
) -> Union[Type[Metadata], Type[NoteMetadata], None]:
    if meta_type == MetadataType.FRONTMATTER:
        return Frontmatter
    elif meta_type == MetadataType.INLINE:
        return InlineMetadata
    elif meta_type == MetadataType.ALL:
        return NoteMetadata
    else:
        return None
        # raise NotImplementedError(f'no metadata class implemented of type "{meta_type}"')
