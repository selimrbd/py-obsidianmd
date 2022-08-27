"""Defines exceptions used in other modules."""

from string import Template
from typing import Union


class InvalidFrontmatterError(ValueError):
    """The frontmatter is invalid."""


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
