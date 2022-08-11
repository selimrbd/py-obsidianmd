from __future__ import annotations

import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional, Type, Union

import frontmatter

from .exceptions import ArgTypeError, InvalidFrontmatterError

UserInput = Union[str, int, float]
MetaDict = dict[str, list[str]]
ParseFunction = Callable[[str], tuple[MetaDict, str]]
Number = int | float


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


class MetadataType(Enum):
    FRONTMATTER = "frontmatter"
    INLINE = "inline"
    ALL = "notemeta"

    @staticmethod
    def get_from_str(s: str | None) -> MetadataType:
        if s is None:
            return MetadataType.ALL
        for k in MetadataType:
            if s == k.value:
                return k
        raise ValueError(f'Metadatatype not defined: "{s}"')


class Metadata(ABC):
    def __init__(self, note_content: str):
        parsed = self.parse(note_content)
        self.metadata: MetaDict = parsed[0]
        self._content_no_meta = parsed[1]

    def __repr__(self):
        r = f"{type(self)}:\n"
        if self.to_string() is None:
            r += " None"
        else:
            r += "".join([f'- {k}: {", ".join(v)}\n' for k, v in self.metadata.items()])
        return r

    @classmethod
    @abstractmethod
    def parse(
        cls, note_content: str, parse_fn: ParseFunction | None = None
    ) -> tuple[MetaDict, str]:
        pass

    @abstractmethod
    def to_string(self) -> str:
        """Render metadata as a string.

        If repr is True, print to screen
        """
        pass

    @abstractmethod
    def update_content(self, note_content: str) -> str:
        ...

    @classmethod
    def exists(cls, note_content: str) -> bool:
        """Checks if the metadata type is present in the note"""
        try:
            meta_dict = cls.parse(note_content)[0]
        except:
            meta_dict = {}
        return len(meta_dict) > 0

    def add(
        self,
        k: str,
        l: Union[UserInput, list[UserInput], None],
        overwrite: bool = False,
    ) -> None:
        """adds a metadata field, or new values if it already exists

        If overwrite is set to True, the old value is overwritten. Otherwise, new elements are
        appended.
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
                self.metadata[k] += nl
            else:
                self.metadata[k] = nl

    def remove(
        self, k: str, l: Optional[Union[UserInput, list[UserInput]]] = None
    ) -> None:
        """removes a metadata field"""
        if k not in self.metadata:
            return
        if l is None:
            del self.metadata[k]
            return
        nl = [str(l)] if isinstance(l, UserInput) else [str(x) for x in l]
        self.metadata[k] = [e for e in self.metadata[k] if e not in nl]

    def remove_duplicate_values(self, k: str | list[str] | None = None) -> None:

        if k is None:
            list_keys = list(self.metadata.keys())
        elif isinstance(k, str):
            list_keys = [k]
        elif isinstance(k, list):
            list_keys = k
        else:
            raise ArgTypeError("k", type(k), str(Optional[str | list[str]]))

        for k2 in list_keys:
            if k2 not in self.metadata:
                continue
            self.metadata[k2] = list(dict.fromkeys(self.metadata[k2]))

    def order_values(
        self, k: str | list[str] | None = None, how: Order = Order.ASC
    ) -> None:
        """Orders metadata values.

        Attributes:
            - k: key on which to order the values. If None, orders all values
        """
        if not isinstance(how, Order):
            raise ArgTypeError("how", type(how), Order)  # type: ignore

        if k is None:
            k = list(self.metadata.keys())
        if isinstance(k, str):
            k = [k]
        for e in k:
            reverse = False if (how == Order.ASC) else True
            self.metadata[e] = sorted(self.metadata[e], reverse=reverse)

    def order_keys(self, how: Order = Order.ASC) -> None:
        """Orders metadata keys.

        Utilizes that since 3.6, python dict remember insert order.
        """
        reverse = how == Order.DESC
        list_keys = sorted(list(self.metadata.keys()), reverse=reverse)
        self.metadata = {k: self.metadata.pop(k) for k in list_keys}

    def order(
        self,
        k: str | list[str] | None = None,
        o_keys: Order | None = Order.ASC,
        o_values: Order | None = Order.ASC,
    ):
        """Orders metadata keys and values.

        Attributes:
            - keys: keys for which to order the values
            - o_keys: how to order the keys. If None, don't order them
            - o_values: how to order values. If None, don't order them
        """
        if o_keys is not None:
            self.order_keys(how=o_keys)
        if o_values is not None:
            self.order_values(k=k, how=o_values)
        return None

    def print(self):
        print(self.to_string())


class Frontmatter(Metadata):
    """Represents the frontmatter of a note"""

    @classmethod
    def parse(
        cls, note_content: str, parse_fn: ParseFunction | None = None
    ) -> tuple[MetaDict, str]:
        """Parse note content to extract metadata dictionary."""
        if parse_fn is None:
            parse_fn = cls.parse_1
        return parse_fn(note_content)

    @staticmethod
    def parse_1(note_content: str) -> tuple[MetaDict, str]:
        """Parse note content to extract metadata dictionary.
        Uses the python-frontmatter library."""
        try:
            fm = frontmatter.loads(note_content)
        except:
            raise InvalidFrontmatterError

        meta_dict: MetaDict = fm.metadata
        content_no_meta = fm.content

        # make all elements into list of strings
        for k, v in meta_dict.items():
            if isinstance(v, str):
                meta_dict[k] = [v]
            if isinstance(v, Number):
                meta_dict[k] = [str(v)]
            if isinstance(v, list):
                meta_dict[k] = [str(x) for x in v]
        # parse special fields
        for k in ["tag", "tags"]:
            sep = "__sep__"
            sep_chr = [",", " "]
            if k in meta_dict:
                res: list[str] = list()
                for e in meta_dict[k]:
                    for sc in sep_chr:
                        e = re.sub(re.escape(sc), sep, e)
                    res += [x.strip() for x in e.split(sep) if len(x.strip()) > 0]
                meta_dict[k] = res
        return meta_dict, content_no_meta

    @staticmethod
    def parse_2(note_content: str) -> tuple[MetaDict, str]:
        """Parse frontmatter metadata using regex"""
        regex = "(?s)(^---\n).*?(\n---\n)"
        mtc = re.search(regex, note_content)
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

        content_no_meta = re.sub(regex, "", note_content)
        return metadata, content_no_meta

    def to_string(self) -> str:
        """Render metadata as a string.

        If repr is True, print to screen
        """
        if len(self.metadata) == 0:
            return ""
        metadata_repr = [f"{k}: {', '.join(v)}\n" for k, v in self.metadata.items()]
        out = "---\n" + "".join(metadata_repr) + "---\n\n"
        return out

    def update_content(self, note_content: str) -> str:
        """ """
        res = self.to_string() + self._content_no_meta
        return res


class InlineMetadata(Metadata):
    """Represents the inline metadata of a note"""

    REGEX = "[A-z]\w+ ?::.*"

    @staticmethod
    def _extract_str(note_content: str) -> list[str]:
        return re.findall(InlineMetadata.REGEX, note_content)

    @staticmethod
    def _str_to_dict(meta_str: list[str]) -> MetaDict:
        metadata: MetaDict = dict()
        tmp: dict[str, str] = dict()
        for x in meta_str:
            k, v = x.split("::")[0].strip(), x.split("::")[1].strip()
            if k not in tmp:
                tmp[k] = v
            else:
                tmp[k] += f", {v}"
        metadata = {k: [x.strip() for x in v.split(",")] for (k, v) in tmp.items()}
        if "tags" in metadata:
            mtags = " ".join(metadata["tags"])
            metadata["tags"] = [t.strip() for t in mtags.split(" ") if t.strip() != ""]
        return metadata

    def to_string(self) -> str:
        """Render metadata as a string.

        If repr is True, print to screen
        """
        if len(self.metadata) == 0:
            return ""
        r = "\n\n---\n- **@ metadata:**\n"
        for k, v in self.metadata.items():
            r += f"    - {k}:: {', '.join(v)}\n"
        return r

    def update_content(self, note_content: str) -> str:
        """ """
        res = self.erase(note_content)
        res = res + self.to_string()
        return res


class NoteMetadata:
    """Contains all the note's metadata (frontmatter + inline)."""

    def __init__(self, note_content: str):
        self.frontmatter = Frontmatter(note_content)
        self.inline = InlineMetadata(note_content)

    @classmethod
    def _parse_arg_meta_type(cls, meta_type: MetadataType | None) -> MetadataType:
        if meta_type is None:
            meta_type = MetadataType.ALL
        if not isinstance(meta_type, MetadataType):  # type: ignore
            raise ArgTypeError(
                var_name="meta_type",
                given_type=type(meta_type),
                expected_type=str(MetadataType | None),
            )
        return meta_type

    def add(
        self,
        k: str,
        l: Union[UserInput, list[UserInput], None],
        meta_type: MetadataType = MetadataType.FRONTMATTER,
        overwrite: bool = False,
    ) -> None:
        """ """
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.add(k=k, l=l, overwrite=overwrite)
        if meta_type == MetadataType.INLINE:
            self.inline.add(k=k, l=l, overwrite=overwrite)

    def remove(
        self,
        k: str,
        l: Optional[Union[UserInput, list[UserInput]]] = None,
        meta_type: MetadataType = MetadataType.FRONTMATTER,
    ) -> None:
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.remove(k=k, l=l)
        if meta_type == MetadataType.INLINE:
            self.inline.remove(k=k, l=l)

    def remove_duplicate_values(
        self, k: str | list[str] | None, meta_type: MetadataType | None = None
    ):
        """Remove duplicate values in the note's metadata

        Attributes:
            - k: key or list of keys on which to perform the duplication removal. If None, do on all keys
            - meta_type: target Metadata type. If None, does it on all metadata
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

    def update_content(
        self, note_content: str, meta_type: MetadataType | None = None
    ) -> str:
        meta_type = self._parse_arg_meta_type(meta_type)
        res = note_content
        if meta_type == MetadataType.FRONTMATTER:
            res = self.frontmatter.update_content(res)
        elif meta_type == MetadataType.INLINE:
            res = self.inline.update_content(res)
        elif meta_type == MetadataType.ALL:
            res = self.frontmatter.update_content(res)
            res = self.inline.update_content(res)
        else:
            raise ValueError(f"Unsupported value for argument meta_type: {meta_type}")
        return res

    def order_values(
        self,
        k: str | list[str] | None = None,
        how: Order = Order.ASC,
        meta_type: MetadataType | None = None,
    ) -> None:
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
        self, how: Order = Order.DESC, meta_type: MetadataType | None = None
    ) -> None:
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
        k: str | list[str] | None = None,
        o_keys: Order | None = Order.ASC,
        o_values: Order | None = Order.ASC,
        meta_type: MetadataType | None = None,
    ):
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


def return_metaclass(
    meta_type: MetadataType,
) -> Type[Metadata] | Type[NoteMetadata] | None:
    if meta_type == MetadataType.FRONTMATTER:
        return Frontmatter
    elif meta_type == MetadataType.INLINE:
        return InlineMetadata
    elif meta_type == MetadataType.ALL:
        return NoteMetadata
    else:
        return None
        # raise NotImplementedError(f'no metadata class implemented of type "{meta_type}"')
