"""Defines exceptions used in other modules."""

from pathlib import Path
from string import Template
from typing import Union


class InvalidFrontmatterError(Exception):
    """The frontmatter is invalid."""

    def __init__(self, exception: Exception):
        self.exception = exception
        self.msg = f"Error while parsing frontmatter!. Exception:\n{self.exception}"
        super().__init__(self.msg)


class ParsingNoteMetadataError(Exception):
    """Error while parsing a note's metadata."""

    def __init__(self, path: Union[Path, str], exception: Exception):
        self.path = path
        self.exception = exception
        self.msg = f'Error while parsing metadata for note at path: "{self.path}". Exception:\n{self.exception}'
        super().__init__(self.msg)


class NoteCreationError(Exception):
    """Error while creating a note object."""

    def __init__(self, path: Union[Path, str], exception: Exception):
        self.path = path
        self.exception = exception
        self.msg = f'Error while creating Note object for path: "{self.path}". Exception:\n{self.exception}'
        super().__init__(self.msg)


class UpdateContentError(Exception):
    """Error when updating the content of a note."""

    def __init__(self, path: Union[Path, str], exception: Exception):
        self.path = path
        self.exception = exception
        self.msg = f'Error while updating the content of the note: "{self.path}". Exception:\n{self.exception}'
        super().__init__(self.msg)


class ArgTypeError(Exception):
    """The argument isn't of the expected type."""

    def __init__(
        self, var_name: str, type_given: type, type_expected: Union[type, str]
    ):
        self.var_name = var_name
        self.type_given = type_given
        self.type_expected = type_expected
        tml = Template("variable '$v' type is not valid.\ntype: $g\nexpected type: $e")
        msg = tml.substitute(v=self.var_name, g=self.type_given, e=self.type_expected)
        super().__init__(msg)
