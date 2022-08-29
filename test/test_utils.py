import difflib
import json
import os
from pathlib import Path
from string import Template
from typing import Union

PATH_TEST_DATA = Path(__file__).parent / "0-test-data"
PATH_TEST_NOTES = PATH_TEST_DATA / "notes"

from pyomd.metadata import MetadataType, Order


def load_test_notes(path_test_notes: Union[Path, None]) -> dict:
    """ """
    data = dict()
    if path_test_notes is None:
        return data
    note_dirs = os.listdir(path_test_notes)
    for nd in note_dirs:
        path_nd = path_test_notes / nd
        data[nd] = {"path": path_nd / f"{nd}.md"}
        with open(data[nd]["path"], "r") as f:
            data[nd]["content"] = f.read()
        md_files = [
            x
            for x in os.listdir(path_nd)
            if x.endswith(".md") and x != data[nd]["path"].name
        ]
        for mdf in md_files:
            path_mdf = path_nd / mdf
            field_name = Path(mdf).stem.split("-", maxsplit=1)[-1]
            with open(path_mdf, "r") as f:
                data[nd][field_name] = f.read()
    return data


def load_test_definitions(path_test_def: Path) -> dict:
    with open(path_test_def, "r") as f:
        test_def = json.load(f)
    return test_def


def load_data(
    path_test_def: Path, path_test_notes: Union[Path, None] = PATH_TEST_NOTES
) -> dict:
    data = load_test_notes(path_test_notes)
    data.update(load_test_definitions(path_test_def))
    return data


### parse arguments


def get_test_arg_meta_type(
    test_id: str, name_f: str, data: dict
) -> Union[MetadataType, str, None]:
    meta_type_str: str = data["tests"].get("default_meta_type", None)
    meta_type_str = data["tests"][f"tests-{name_f}"][test_id]["inputs"].get(
        "meta_type", meta_type_str
    )
    if meta_type_str is None:
        return None
    return parse_test_arg_meta_type(meta_type_str)


def parse_test_arg_meta_type(
    meta_type_str: Union[str, None]
) -> Union[MetadataType, str, None]:
    if meta_type_str == ">>MetadataType.FRONTMATTER":
        meta_type = MetadataType.FRONTMATTER
    elif meta_type_str == ">>MetadataType.INLINE":
        meta_type = MetadataType.INLINE
    elif meta_type_str == ">>MetadataType.ALL":
        meta_type = MetadataType.ALL
    else:
        meta_type = meta_type_str
    return meta_type


def parse_test_arg_order(order_str: str) -> Union[Order, str]:
    if order_str == ">>Order.ASC":
        order = Order.ASC
    elif order_str == ">>Order.DESC":
        order = Order.DESC
    else:
        order: Union[str, Order] = order_str
    return order


def parse_name_function_tested(name_f: str):
    return name_f.split("_", maxsplit=1)[-1]


### assertions


def build_error_msg(test_id: str, dict_tests: dict) -> str:
    templ = "\n-- TEST FAILED --\n"
    templ += f'test ID: "$test_id"\n'
    templ += 'test description: "$test_desc"'
    templ = Template(templ)
    err_msg = templ.substitute(test_id=test_id, test_desc=dict_tests["description"])
    return err_msg


def assert_dict_match(
    d1: Union[dict, None], d2: Union[dict, None], msg: str = ""
) -> None:
    """
    assert that 2 dictionaries match. If they dont, print the output VS expected
    Arguments:
        - d1: output of function to test
        - d2: expected result
        - msg: additional message to display at the beginning of the assertion error
    """
    d1 = dict() if d1 is None else d1
    d2 = dict() if d2 is None else d2
    err_template = Template(
        "$msg\n---\ndictionaries don't match.\nkey: '$k'\noutput: '$o'\nexpected result: '$er'\n"
    )
    for k in set(d1.keys()).union(set(d2.keys())):
        o = d1.get(k, None)
        er = d2.get(k, None)
        err_msg = err_template.substitute(msg=msg, k=k, o=o, er=er)
        assert o == er, err_msg


def assert_str_match(s1: str, s2: str, msg: str = "") -> None:
    """
    assert that 2 strings match. If they dont, print the output VS expected
    Arguments:
        - s1: output of function to test
        - s2: expected result
    """
    diffs = difflib.unified_diff(
        s1.split("\n"),
        s2.split("\n"),
        fromfile="output",
        tofile="expected result",
        lineterm="",
    )
    err_msg = "\n".join(["strings don't match."] + list(diffs))
    assert s1 == s2, err_msg


def assert_list_match(
    l1: list, l2: list, msg: str = "", respect_order: bool = True
) -> None:
    """
    assert that 2 lists match. If they dont, print the output VS expected
    Arguments:
        - l1: output of function to test
        - l2: expected result
    """
    l1 = list() if l1 is None else l1
    l2 = list() if l2 is None else l2
    err_template = Template(
        "$msg\n---\nlists don't match.\noutput: $o\nexpected result: $er\n"
    )
    err_msg = err_template.substitute(msg=msg, o=l1, er=l2)
    if respect_order:
        assert l1 == l2, err_msg
    else:
        b1 = all(x in l2 for x in l1)
        b2 = all(x in l1 for x in l2)
        assert b1 and b2, err_msg
