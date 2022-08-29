import inspect
from functools import partial
from pathlib import Path
from typing import Callable, Union

from pyomd.metadata import MetadataType
from pyomd.note import Notes

from ..test_utils import (
    assert_list_match,
    build_error_msg,
    parse_name_function_tested,
    parse_test_arg_meta_type,
)

PATH_TEST_DATA = Path(__file__).parent / "../0-test-data"
PATH_TEST_NOTES = PATH_TEST_DATA / "notes"


TestTemplateNote = Callable[[str, dict, bool], None]


def add_test_function_note(glob: dict, fn: TestTemplateNote, test_id: str, data: dict):

    ft = partial(fn, test_id=test_id, data=data)
    name_f = parse_name_function_tested(fn.__name__)
    ft_name = f"test_{name_f}_{test_id}"
    glob[ft_name] = ft


def prep_test_data_note(test_id: str, data: dict, name_f: str):
    d_t: dict = data["tests"][f"tests-{name_f}"][test_id]

    inputs: dict = d_t["inputs"]
    expected_output: dict = d_t["expected_output"]

    return inputs, expected_output, d_t


def parse_test_arg_has_meta(
    has_meta: Union[None, list[list[str]]],
) -> Union[None, list[tuple[str, Union[None, list[str]], MetadataType]]]:
    if has_meta is None:
        return None
    return [(x[0], x[1], parse_test_arg_meta_type(x[2])) for x in has_meta]


##


def t___init__(test_id: str, data: dict, debug: bool = False):

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_t = prep_test_data_note(test_id, data, name_f)

    input_paths = [PATH_TEST_NOTES / x for x in inputs["paths"]]
    nts = Notes(paths=input_paths, recursive=inputs["recursive"])
    paths = [note.path.name for note in nts.notes]
    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(
        l1=paths, l2=expected_output["paths"], msg=err_msg, respect_order=False
    )


def t_filter(test_id: str, data: dict, debug: bool = False):

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_t = prep_test_data_note(test_id, data, name_f)

    arg_input_paths = [PATH_TEST_NOTES / x for x in inputs["paths"]]
    arg_recursive = inputs["recursive"]
    arg_starts_with = inputs["starts_with"]
    arg_ends_with = inputs["ends_with"]
    arg_pattern = inputs["pattern"]
    arg_has_meta = parse_test_arg_has_meta(inputs["has_meta"])
    nts = Notes(paths=arg_input_paths, recursive=arg_recursive)
    nts.filter(
        starts_with=arg_starts_with,
        ends_with=arg_ends_with,
        pattern=arg_pattern,
        has_meta=arg_has_meta,
    )

    paths = [note.path.name for note in nts.notes]
    paths_true = expected_output["paths"]

    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(l1=paths, l2=paths_true, msg=err_msg, respect_order=False)
