from string import Template
from typing import Union


class InvalidFrontmatterError(ValueError):
    def __init__(self):
        super().__init__()


class ArgTypeError(Exception):
    def __init__(
        self, var_name: str, given_type: type, expected_type: Union[type, str]
    ):
        self.var_name = var_name
        self.given_type = given_type
        self.expected_type = expected_type
        t = Template("variable '$v' type is not valid.\ntype: $g\nexpected type: $e")
        msg = t.substitute(v=self.var_name, g=self.given_type, e=self.expected_type)
        super().__init__(msg)
