import inspect
from functools import partial
from pathlib import Path
from typing import Callable, Type, Union

import pytest

from pyomd.exceptions import InvalidFrontmatterError  # pylance: ignore
from pyomd.metadata import (
    InlineMetadata,
    MetadataType,
    NoteMetadata,
    Order,
    return_metaclass,
)

from ..test_utils import (
    assert_dict_match,
    assert_list_match,
    assert_str_match,
    build_error_msg,
    get_test_arg_meta_type,
    parse_name_function_tested,
    parse_test_arg_meta_type,
    parse_test_arg_order,
)

PATH_TEST_DATA = Path(__file__).parent / "../0-test-data"
PATH_TEST_NOTES = PATH_TEST_DATA / "notes"

###

TestTemplateMetadata = Callable[[str, dict, bool], None]


def add_test_function_metadata(
    glob: dict,
    fn: TestTemplateMetadata,
    test_id: str,
    data: dict,
    meta_type: Union[MetadataType, None] = None,
):
    """Adds a test function to the global environment.

    Tests related to the Metadata object.

    Args:
        glob:
            dictionary of global variables (returned by globals())
        fn:
            test template function.
            Takes as arguments:
                test_id: the test ID
                data: dictionary of data returned by
                debug: activate debug mode
        test_id: the test ID
        data: dict containing note and test data
        meta_type: metadata type
    """
    ft = partial(fn, test_id=test_id, data=data)
    name_f = parse_name_function_tested(fn.__name__)
    if meta_type is None:
        meta_type = get_test_arg_meta_type(test_id=test_id, name_f=name_f, data=data)
    ft_name = f"test_{meta_type.value}_{name_f}_{test_id}"
    glob[ft_name] = ft


def prep_test_data(test_id: str, data: dict, name_f: str):
    d_t: dict = data["tests"][f"tests-{name_f}"][test_id]
    inputs: dict = d_t["inputs"]

    note_name: str = d_t["data"]
    d_n: dict = data[note_name]

    expected_output: dict = d_t["expected_output"]

    meta_type = get_test_arg_meta_type(test_id=test_id, name_f=name_f, data=data)
    MetaClass = return_metaclass(meta_type)

    return inputs, expected_output, d_n, d_t, MetaClass


### metadata test templates


def t_parse(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    if "exception" in expected_output:
        exception: Type[Exception] = globals()[expected_output["exception"]]
        with pytest.raises(exception):
            MetaClass._parse(d_n["content"])
    else:
        meta_dict = MetaClass._parse(d_n["content"])
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
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    if isinstance(m, InlineMetadata):
        arg_pos: str = inputs["position"]
        arg_inplace: bool = inputs["inplace"]
        upd: str = m._update_content(d_n["content"], position=arg_pos, inplace=arg_inplace)  # type: ignore
    else:
        upd: str = m._update_content(d_n["content"])  # type: ignore
    name_field_true: str = expected_output["field_name"]
    upd_true: str = d_n[name_field_true]

    if debug:
        return upd, upd_true
    err_msg = build_error_msg(test_id, d_t)
    if isinstance(m, InlineMetadata):
        err_msg = f'arg_pos: "{arg_pos}"\narg_inplace: "{arg_inplace}"\n' + err_msg
    assert_str_match(upd, upd_true, msg=err_msg)


def t_exists(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    _, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    exists: bool = MetaClass._exists(d_n["content"])  # type: ignore
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


def t_remove_and_update(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n["content"])
    arg_k = inputs["k"]
    arg_l = inputs["l"]
    arg_inplace = inputs["inplace"]
    arg_pos = inputs["position"]
    m.remove(k=arg_k, l=arg_l)  # type: ignore
    note_content = m._update_content(
        d_n["content"], inplace=arg_inplace, position=arg_pos
    )

    name_field_true: str = expected_output["field_name"]
    note_content_true: str = d_n[name_field_true]

    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(s1=note_content, s2=note_content_true, msg=err_msg)


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

    ers: str = MetaClass._erase(d_n["content"])  # type: ignore
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


def nmt_has(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])
    meta_type = parse_test_arg_meta_type(inputs["meta_type"])
    b_has = m.has(k=inputs["k"], l=inputs["l"], meta_type=meta_type)
    b_has_true = expected_output["b_has"]
    err_msg = build_error_msg(test_id, d_t)
    assert b_has == b_has_true, f"b_has: {b_has}\nb_has_true: {b_has_true}\n{err_msg}"


def nmt_get(test_id: str, data: dict, debug: bool = False) -> None:

    name_f = parse_name_function_tested(inspect.currentframe().f_code.co_name)
    inputs, expected_output, d_n, d_t, _ = prep_test_data(test_id, data, name_f)

    m = NoteMetadata(d_n["content"])

    arg_k = inputs["k"]
    arg_meta_type = parse_test_arg_meta_type(inputs["meta_type"])

    res = m.get(k=arg_k, meta_type=arg_meta_type)
    res_true = expected_output["out"]
    err_msg = build_error_msg(test_id, d_t)
    assert_list_match(l1=res, l2=res_true, msg=err_msg)


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

    arg_content: str = d_n["content"]
    arg_inline_pos: str = inputs["inline_position"]
    arg_inline_inplace: bool = inputs["inline_inplace"]
    nb_times = int(inputs.get("nb_times", 1))

    m = NoteMetadata(arg_content)
    for _ in range(nb_times):
        upd: str = m._update_content(
            note_content=arg_content,
            inline_position=arg_inline_pos,
            inline_inplace=arg_inline_inplace,
        )  # type: ignore
    name_field_true: str = expected_output["field_name"]
    upd_true: str = d_n[name_field_true]

    if debug:
        return (upd, upd_true)

    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(upd, upd_true, msg=err_msg)
