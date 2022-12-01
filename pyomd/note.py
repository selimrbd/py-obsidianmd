"""Note objects."""

import os
import re
from pathlib import Path
from typing import Callable, Optional, Union

from pyomd.metadata import MetadataType, NoteMetadata, NoteMetadataBatch

from .exceptions import NoteCreationError, ParsingNoteMetadataError, UpdateContentError


class Note:
    """A Markdown note.

    Attributes:
        path:
            path to the note.
        metadata:
            NoteMetadata object.
        content:
            The note's textual content (including all types of metadata).
    """

    def __init__(self, path: Union[Path, str]):
        """Initializes a Note object.

        Args:
            path: path to the markdown note.
        """
        self.path: Path = Path(path)
        try:
            with open(self.path, "r") as f:
                self.content: str = f.read()
        except Exception as e:
            raise NoteCreationError(path=path, exception=e) from e

        try:
            self.metadata: NoteMetadata = NoteMetadata(self.content)
        except Exception as e:
            raise ParsingNoteMetadataError(path=path, exception=e) from e

    def __repr__(self) -> str:
        return f'Note (path: "{self.path}")\n'

    def append(self, str_append: str, allow_repeat: bool = False):
        """Appends text to the note content.

        Args:
            str_append: string to append to the note content.
            allow_repeat: Add the string if it is already present in the note content.
        """
        if allow_repeat:
            self.content += f"\n{str_append}"
        else:
            if len(re.findall(re.escape(str_append), self.content)) == 0:
                self.content += f"\n{str_append}"

    def print(self):
        """Prints the note content to the screen."""
        print(self.content)

    def sub(self, pattern: str, replace: str, is_regex: bool = False):
        """Substitutes text within the note.

        Args:
            pattern:
                the pattern to replace (plain text or regular expression)
            replace:
                what to replace the pattern with
            is_regex:
                Whether the pattern is a regex pattern or plain text.
        """
        if not is_regex:
            pattern = re.escape(pattern)
        self.content = re.sub(pattern, replace, self.content)

    def update_content(
        self,
        inline_position: str = "bottom",
        inline_inplace: bool = True,
        inline_tml: Union[str, Callable] = "standard",  # type: ignore
        write: bool = False,
    ):
        """Updates the note's content.

        Args:
            inline_position:
                if "bottom" / "top", inline metadata is grouped at the bottom/top of the note.
                This is always the case for new inline metadata (that didn't exist in the
                previous note content).
            inline_inplace:
                By default it is True, which means the inline metadata position in the note
                is not modified. If False, the metadata is grouped according to `inline_how`
            inline_tml:
                Which template to use to update inline metadata content.
                Current possible values: ["standard", "callout"]
                Defaults to "standard": each metadata field is written on a newline.
                "callout": metadata fields are regrouped inside a callout:
                    > [!info]- metadata
                    > key1 :: values1
                    > key2 :: values2
                    ...
                NOTE: In later updates it will be possible to pass a function specifying how
                to display the metadata, for greater customization.
            write:
                Write changes to the file on disk after updating the content.
                If write = False, the user needs to call Note.write() subsequently to write
                changes to disk, otherwise only the self.content attribute is modified
                (in memory, but not on disk).
        """

        try:
            self.content = self.metadata._update_content(
                self.content,
                inline_position=inline_position,
                inline_inplace=inline_inplace,
                inline_tml=inline_tml,
            )
        except Exception as e:
            raise UpdateContentError(path=self.path, exception=e)
        if write:
            self.write()

    def write(self, path: Union[Path, None] = None):
        """Writes the note's content to disk.

        Args:
            path:
                path to the note. If None, overwrites the current note content.
        """
        p = self.path if path is None else path
        with open(p, "w") as f:
            f.write(self.content)

    @staticmethod
    def _is_md_file(path: Path):
        exist = path.exists()
        is_md = path.suffix == ".md"
        return exist and is_md


class Notes:
    """A batch of notes.

    Attributes:
        self.notes:
            list of Note objects
        self.metadata:
            NoteMetadataBatch object
    """

    def __init__(self, paths: Union[Path, list[Path]], recursive: bool = True):
        """Initializes a Notes object.

        Add paths to individual notes or to directories containing multiple notes.

        Args:
            paths:
                list of paths pointing to markdown notes or folders
            recursive:
                When given a path to a directory, whether to add notes
                from sub-directories too
        """
        self.notes: list[Note] = []
        self.add(paths=paths, recursive=recursive)
        self.metadata = NoteMetadataBatch(self.notes)

    def __len__(self):
        return len(self.notes)

    def add(self, paths: Union[Path, list[Path]], recursive: bool = True):
        """Adds new notes to the Notes object.

        Args:
            paths:
                list of paths pointing to markdown notes or folders
            recursive:
                When given a path to a directory, whether to add notes
                from sub-directories too
        """
        if isinstance(paths, Path):
            paths = [paths]
        for pth in paths:
            assert pth.exists(), f"file or folder doesn't exist: '{pth}'"
            if pth.is_dir():
                for root, _, fls in os.walk(pth):  # type: ignore
                    for f_name in fls:  # type: ignore
                        pth_f: Path = Path(root) / f_name  # type: ignore
                        if Note._is_md_file(pth_f):
                            self.notes.append(Note(path=pth_f))
                    if not recursive:
                        break
            elif Note._is_md_file(pth):
                self.notes.append(Note(path=pth))

    def append(self, str_append: str, allow_repeat: bool = False):
        """Appends text to the note content.

        See `Note.append` for argument details."""
        for note in self.notes:
            note.append(str_append=str_append, allow_repeat=allow_repeat)

    def filter(
        self,
        starts_with: Optional[str] = None,
        ends_with: Optional[str] = None,
        pattern: Optional[str] = None,
        has_meta: Optional[
            list[tuple[str, Union[list[str], str, None], Optional[MetadataType]]]
        ] = None,
    ):
        """Keep only notes that have certain characteristics.

        Args:
            starts_with:
                Keep notes which file name starts with the string
            ends_with:
                Keep notes which file name ends with the string
            pattern:
                Keep notes which file name matches the regex pattern
            has_meta:
                keep notes which contains the specified metadata.
                has_meta is a list of tuples:
                (key_name, l_values, meta_type)
                that correspond to the arguments of NoteMetadata.has()
        """
        if starts_with is not None:
            self.notes = [
                n for n in self.notes if str(n.path.name).startswith(starts_with)
            ]
        if ends_with is not None:
            self.notes = [n for n in self.notes if str(n.path.name).endswith(ends_with)]
        if pattern is not None:
            self.notes = [n for n in self.notes if re.match(pattern, str(n.path.name))]
        if has_meta is not None:
            include: list[bool] = []
            for note in self.notes:
                inc = True
                for (k, vals, meta_type) in has_meta:
                    if not note.metadata.has(k=k, l=vals, meta_type=meta_type):
                        inc = False
                include.append(inc)
            self.notes = [n for (n, inc) in zip(self.notes, include) if inc]

    def update_content(
        self,
        inline_position: str = "bottom",
        inline_inplace: bool = True,
        inline_tml: Union[str, Callable] = "standard",  # type: ignore
        write: bool = False,
    ):
        """Updates the content of all notes.

        See `Note.update_content` for argument details.
        """
        for note in self.notes:
            note.update_content(
                inline_position=inline_position,
                inline_inplace=inline_inplace,
                inline_tml=inline_tml,
                write=write,
            )

    def write(self):
        """Writes the note's content to disk.

        See `Note.write` for argument details.
        """
        for note in self.notes:
            note.write()
