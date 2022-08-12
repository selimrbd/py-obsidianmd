import sys
from pathlib import Path

sys.path.append("../..")
import inspect
from functools import partial
from string import Template
from typing import Callable, Type

import pytest
from source.exceptions import InvalidFrontmatterError
from source.metadata import MetadataType, NoteMetadata, Order, return_metaclass

PATH_TEST_DATA = Path(__file__).parent / "../0-test-data"
PATH_TEST_NOTES = PATH_TEST_DATA / "notes"

### utils


def build_error_msg(test_id: str, dict_tests: dict) -> str:
    templ = "\n-- TEST FAILED --\n"
    templ += f'test ID: "$test_id"\n'
    templ += 'test description: "$test_desc"'
    templ = Template(templ)
    err_msg = templ.substitute(test_id=test_id, test_desc=dict_tests["description"])
    return err_msg

def assert_dict_match(d1: dict | None, d2: dict | None, msg: str = "") -> None:
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
    err_template = Template(
        "$msg\n---\nstrings don't match.\n@@ output @@\n$o\n@@@@@\n@@ expected result @@\n$er\n@@@@@\n"
    )
    err_msg = err_template.substitute(msg=msg, o=s1, er=s2)
    assert s1 == s2, err_msg

def assert_list_match(l1: list, l2: list, msg: str = "") -> None:
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
    assert l1 == l2, err_msg


###

TestTemplateMetadata = Callable[[str, dict, MetadataType, bool], None]

def add_test_function_metadata(
    glob: dict,
    fn: TestTemplateMetadata,
    test_id: str,
    data: dict,
    meta_type: MetadataType | None = None,
):
    ft = partial(fn, test_id=test_id, data=data)
    name_f = parse_name_function_tested(fn.__name__)
    if meta_type is None:
        meta_type = get_test_arg_meta_type(test_id=test_id, name_f=name_f, data=data)
    ft_name = f"test_{meta_type.value}_{name_f}_{test_id}"
    glob[ft_name] = ft

def prep_test_data(test_id: str, data: dict, name_f: str):
    d_t: dict = data["tests"][f"tests-{name_f}"][test_id]
    inputs: dict = d_t["inputs"]
    meta_type = get_test_arg_meta_type(test_id=test_id, name_f=name_f, data=data)
    note_name: str = d_t["data"]
    d_n: dict = data[note_name]
    expected_output: dict = d_t["expected_output"]
    MetaClass = return_metaclass(meta_type)

    return inputs, expected_output, d_n, d_t, MetaClass

### parse arguments

def get_test_arg_meta_type(
    test_id: str, name_f: str, data: dict
) -> MetadataType | str | None:
    meta_type_str: str = data["tests"].get("default_meta_type", None)
    meta_type_str = data["tests"][f"tests-{name_f}"][test_id]["inputs"].get(
        "meta_type", meta_type_str
    )
    if meta_type_str is None:
        return None
    return parse_test_arg_meta_type(meta_type_str)

def parse_test_arg_meta_type(meta_type_str: str | None) -> MetadataType | str | None:
    if meta_type_str == ">>MetadataType.FRONTMATTER":
        meta_type = MetadataType.FRONTMATTER
    elif meta_type_str == ">>MetadataType.INLINE":
        meta_type = MetadataType.INLINE
    elif meta_type_str == ">>MetadataType.ALL":
        meta_type = MetadataType.ALL
    else:
        meta_type = meta_type_str
    return meta_type

def parse_test_arg_order(order_str: str) -> Order | str:
    if order_str == ">>Order.ASC":
        order = Order.ASC
    elif order_str == ">>Order.DESC":
        order = Order.DESC
    else:
        order: str | Order = order_str
    return order

def parse_name_function_tested(name_f: str):
    return name_f.split("_", maxsplit=1)[-1]


### metadata test templates


def t_parse(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    if "exception" in expected_output:
        exception: Type[Exception] = globals()[expected_output["exception"]]
        with pytest.raises(exception):
            MetaClass.parse(d_n["content"])
    else:
        meta_dict = MetaClass.parse(d_n["content"])
        meta_dict_true = expected_output["meta_dict"]

        if debug:
            return meta_dict, meta_dict_true
        err_msg = build_error_msg(test_id, d_t)
        assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t__extract_str(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, _, MetaClass = prep_test_data(test_id, data, name_f)

    str_exr: list[str] = MetaClass._extract_str(d_n["content"])  # type: ignore
    str_exr_true: list[str] = expected_output["str_extracted"]

    if debug:
        return str_exr, str_exr_true
    assert_list_match(str_exr, str_exr_true)

def t__str_to_dict(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, _, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    meta_dict: dict = MetaClass._str_to_dict(inputs["str_extracted"])  # type: ignore
    meta_dict_true: dict = expected_output["meta_dict"]

    if debug:
        return meta_dict, meta_dict_true
    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_to_string(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    tostr: str = m.to_string()  # type: ignore
    name_field_true: str = expected_output["field_name"]
    tostr_true: str = d_n[name_field_true]

    if debug:
        return tostr, tostr_true

    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(tostr, tostr_true, msg=err_msg)

def t_update_content(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    upd: str = m.update_content(d_n["content"])  # type: ignore
    name_field_true: str = expected_output["field_name"]
    upd_true: str = d_n[name_field_true]

    if debug:
        return upd, upd_true
    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(upd, upd_true, msg=err_msg)

def t_exists(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    exists: bool = MetaClass.exists(d_n["content"])  # type: ignore
    exists_true: str = expected_output["exists"]

    if debug:
        return exists, exists_true

    err_msg = build_error_msg(test_id, d_t)
    assert exists == exists_true, err_msg

def t_add(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    m.add(k=inputs["k"], l=inputs["l"], overwrite=inputs["overwrite"])  # type: ignore
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output["meta_dict"]

    if debug:
        return meta_dict, meta_dict_true

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_remove(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    m.remove(k=inputs["k"], l=inputs["l"])  # type: ignore
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output["meta_dict"]

    if debug:
        return meta_dict, meta_dict_true

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_remove_duplicate_values(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    m.remove_duplicate_values(k=inputs["k"])
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output["meta_dict"]

    if debug:
        return meta_dict, meta_dict_true

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_order_values(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)
    how = parse_test_arg_order(inputs["how"])

    m = MetaClass(d_n["content"])
    m.order_values(k=inputs["k"], how=how)
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output["meta_dict"]

    if debug:
        return meta_dict, meta_dict_true

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_order_keys(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)
    how = parse_test_arg_order(inputs["how"])

    m = MetaClass(d_n["content"])
    m.order_keys(how=how)
    keys_order = list(m.metadata.keys())
    keys_order_true: dict[str, list[str]] = expected_output["keys_order"]

    if debug:
        return keys_order, keys_order_true

    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(keys_order, keys_order_true, msg=err_msg)

def t_order(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)
    o_keys = parse_test_arg_order(inputs["o_keys"])
    o_values = parse_test_arg_order(inputs["o_values"])

    m = MetaClass(d_n["content"])
    m.order(k=inputs["k"], o_keys=o_keys, o_values=o_values)

    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output["meta_dict"]
    keys_order = list(m.metadata.keys())
    keys_order_true: list[str] = expected_output["keys_order"]

    if debug:
        return keys_order, keys_order_true, meta_dict, meta_dict_true

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)
    assert_list_match(keys_order, keys_order_true, msg=err_msg)

def t_erase(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    ers: str = MetaClass.erase(d_n["content"])  # type: ignore
    name_field_true: str = expected_output["field_name"]
    ers_true: str = d_n[name_field_true]

    if debug:
        return ers, ers_true
    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(ers, ers_true, msg=err_msg)

### NoteMetadata test templates


def nmt_remove_duplicate_values(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    meta_type = parse_test_arg_meta_type(inputs["meta_type"])
    m.remove_duplicate_values(k=inputs["k"], meta_type=meta_type)
    fm_dict = m.frontmatter.metadata
    il_dict = m.inline.metadata
    fm_dict_true: dict[str, list[str]] = expected_output["frontmatter"]
    il_dict_true: dict[str, list[str]] = expected_output["inline"]

    if debug:
        return (fm_dict, fm_dict_true), (il_dict, il_dict_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(fm_dict, fm_dict_true, msg=err_msg)
    assert_dict_match(il_dict, il_dict_true, msg=err_msg)

def nmt_order_values(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    meta_type = parse_test_arg_meta_type(inputs["meta_type"])
    how = parse_test_arg_order(inputs["how"])
    m.order_values(k=inputs["k"], how=how, meta_type=meta_type)
    fm_dict = m.frontmatter.metadata
    il_dict = m.inline.metadata
    fm_dict_true: dict[str, list[str]] = expected_output["frontmatter"]
    il_dict_true: dict[str, list[str]] = expected_output["inline"]

    if debug:
        return (fm_dict, fm_dict_true), (il_dict, il_dict_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(fm_dict, fm_dict_true, msg=err_msg)
    assert_dict_match(il_dict, il_dict_true, msg=err_msg)

def nmt_order_keys(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    meta_type = parse_test_arg_meta_type(inputs["meta_type"])
    how = parse_test_arg_order(inputs["how"])
    m.order_keys(how=how, meta_type=meta_type)
    fm_list_keys = list(m.frontmatter.metadata.keys())
    il_list_keys = list(m.inline.metadata.keys())
    fm_list_keys_true: list[str] = expected_output["frontmatter"]
    il_list_keys_true: list[str] = expected_output["inline"]

    if debug:
        return (fm_list_keys, fm_list_keys_true), (il_list_keys, il_list_keys_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(fm_list_keys, fm_list_keys_true, msg=err_msg)
    assert_list_match(il_list_keys, il_list_keys_true, msg=err_msg)

def nmt_order(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    k = inputs["k"]
    meta_type: MetadataType = parse_test_arg_meta_type(inputs["meta_type"])
    o_keys: Order = parse_test_arg_order(inputs["o_keys"])
    o_values: Order = parse_test_arg_order(inputs["o_values"])
    m.order(k=k, o_keys=o_keys, o_values=o_values, meta_type=meta_type)
    fm_list_keys = list(m.frontmatter.metadata.keys())
    fm_meta_dict = m.frontmatter.metadata
    il_list_keys = list(m.inline.metadata.keys())
    il_meta_dict = m.inline.metadata
    fm_meta_dict_true: dict[str, list[str]] = expected_output["frontmatter"][
        "meta_dict"
    ]
    fm_list_keys_true: list[str] = expected_output["frontmatter"]["list_keys"]
    il_meta_dict_true: dict[str, list[str]] = expected_output["inline"]["meta_dict"]
    il_list_keys_true: list[str] = expected_output["inline"]["list_keys"]

    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(fm_list_keys, fm_list_keys_true, msg=err_msg)
    assert_list_match(il_list_keys, il_list_keys_true, msg=err_msg)
    assert_dict_match(fm_meta_dict, fm_meta_dict_true, msg=err_msg)
    assert_dict_match(il_meta_dict, il_meta_dict_true, msg=err_msg)

def nmt_move(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    fr = parse_test_arg_meta_type(inputs["fr"])
    to = parse_test_arg_meta_type(inputs["to"])
    m.move(k=inputs["k"], fr=fr, to=to)
    fm_dict = m.frontmatter.metadata
    il_dict = m.inline.metadata
    fm_dict_true: dict[str, list[str]] = expected_output["frontmatter"]
    il_dict_true: dict[str, list[str]] = expected_output["inline"]

    if debug:
        return (fm_dict, fm_dict_true), (il_dict, il_dict_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(fm_dict, fm_dict_true, msg=err_msg)
    assert_dict_match(il_dict, il_dict_true, msg=err_msg)

def nmt_update_content(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    arg_content = d_n["content"]
    arg_how_inline = inputs["how_inline"]
    nb_times = int(inputs.get("nb_times", 1))
    
    m = NoteMetadata(arg_content)
    for _ in range(nb_times):
        upd: str = m.update_content(arg_content, how_inline=arg_how_inline)  # type: ignore
    name_field_true: str = expected_output["field_name"]
    upd_true: str = d_n[name_field_true]

    if debug:
        return (upd, upd_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(upd, upd_true, msg=err_msg)
    