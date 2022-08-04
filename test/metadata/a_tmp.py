import json
import os
import sys
from pathlib import Path
from typing import Any, Type, Union

sys.path.append('../..')
import inspect
import re
from functools import partial
from string import Template
from typing import Callable

from source.metadata import Metadata, MetadataType, return_metaclass

PATH_TEST_DATA = Path(__file__).parent/'../0-test-data'
PATH_TEST_NOTES = PATH_TEST_DATA/'notes'

### load data

def load_test_notes(path_test_notes: Path = PATH_TEST_NOTES) -> dict:
    """
    """
    data = dict()
    note_dirs = os.listdir(path_test_notes)
    for nd in note_dirs:
        path_nd = path_test_notes/nd
        data[nd] = {'path': path_nd/f'{nd}.md'}
        with open(data[nd]['path'], 'r') as f:
            data[nd]['content'] = f.read()
        md_files = [x for x in os.listdir(path_nd) if x.endswith('.md') and x != data[nd]['path'].name]
        for mdf in md_files:
            path_mdf = path_nd/mdf
            field_name = Path(mdf).stem.split('-', maxsplit=1)[-1]
            with open(path_mdf, 'r') as f:
                data[nd][field_name] = f.read()
    return data

def load_test_definitions(path_test_def: Path) -> dict:
    with open(path_test_def, 'r') as f:
        test_def = json.load(f)
    return test_def
    
def load_data(path_test_def: Path, path_test_notes: Path = PATH_TEST_NOTES) -> dict:
    data = load_test_notes(path_test_notes)
    data.update(load_test_definitions(path_test_def))
    return data

### utils

def build_error_msg(test_id: str, dict_tests: dict) -> str:
    templ = "\n-- TEST FAILED --\n" 
    templ += f'test ID: "$test_id"\n'
    templ += 'test description: "$test_desc"'
    templ = Template(templ)
    err_msg = templ.substitute(test_id=test_id, test_desc=dict_tests['description'])
    return err_msg

def get_name_function_tested(fn: Callable):
    return fn.__name__.split('_', maxsplit=1)[-1]

def assert_dict_match(d1: dict|None, d2: dict|None, msg: str='') -> None:
    """
    assert that 2 dictionaries match. If they dont, print the output VS expected
    Arguments:
        - d1: output of function to test
        - d2: expected result
        - msg: additional message to display at the beginning of the assertion error
    """
    d1 = dict() if d1 is None else d1
    d2 = dict() if d2 is None else d2
    err_template = Template("$msg\n---\ndictionaries don't match.\nkey: $k\noutput: $o\nexpected result: $er\n")
    for k in set(d1.keys()).union(set(d2.keys())):
        o = d1.get(k, None)
        er = d2.get(k, None)
        err_msg = err_template.substitute(msg=msg, k=k, o=o, er=er)
        assert (o == er), err_msg

def assert_str_match(s1: str, s2: str, msg: str='') -> None:
    """
    assert that 2 strings match. If they dont, print the output VS expected
    Arguments:
        - s1: output of function to test
        - s2: expected result
    """
    err_template = Template("$msg\n---\nstrings don't match.\n@@ output @@\n$o\n@@@@@\n@@ expected result @@\n$er\n@@@@@\n")
    err_msg = err_template.substitute(msg=msg, o=s1, er=s2)
    assert (s1 == s2), err_msg

def assert_list_match(l1: list, l2: list, msg: str='') -> None:
    """
    assert that 2 lists match. If they dont, print the output VS expected
    Arguments:
        - l1: output of function to test
        - l2: expected result
    """
    l1 = list() if l1 is None else l1
    l2 = list() if l2 is None else l2
    err_template = Template("$msg\n---\nlists don't match.\noutput: $o\nexpected result: $er\n")
    err_msg = err_template.substitute(msg=msg, o=l1, er=l2)
    assert (l1 == l2), err_msg


### TestTemplateMetadata

TestTemplateMetadata = Callable[[str, dict, MetadataType, bool], None]


def add_test_function_fminline(glob: dict, fn: TestTemplateMetadata, test_id: str, data: dict, meta_type: MetadataType):
    ft = partial(fn, test_id=test_id, data=data, meta_type=meta_type)
    name_f_tested = get_name_function_tested(fn)
    name_meta = meta_type.value
    ft_name = f"test_{name_meta}_{name_f_tested}_{test_id}"
    glob[ft_name] = ft

def prep_test_data(test_id: str, data: dict, name_f: str):
    d_t: dict = data["tests"][f'tests-{name_f}'][test_id]
    inputs: dict = d_t['inputs']
    meta_type = get_test_meta_type(test_id=test_id, name_f=name_f, data=data)
    note_name: str = d_t["data"]
    d_n: dict = data[note_name]
    expected_output: dict = d_t['expected_output']
    MetaClass = return_metaclass(meta_type)

    return inputs, expected_output, d_n, d_t, MetaClass


def get_test_meta_type(test_id: str, name_f: str, data: dict) -> MetadataType|None:
    meta_type_str = data["tests"].get('default_meta_type', None)
    meta_type_str = data['tests'][f'tests-{name_f}'][test_id]['inputs'].get('meta_type', meta_type_str)
    if meta_type_str is None: return None
    return MetadataType.get_from_str(meta_type_str)
 

def t__extract_str(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    _ , expected_output, d_n, _ , MetaClass = prep_test_data(test_id, data, name_f)
    # d_t: dict = data["tests"][f'tests-{name_f}'][test_id]
    # inputs = d_t['inputs']
    # meta_type = MetadataType.get_from_str(data["default_meta_type"])
    # if 'meta_type' in inputs: meta_type = MetadataType.get_from_str(inputs["meta_type"])
    # note_name: str = d_t["data"]
    # d_n: dict = data[note_name]
    # expected_output = d_t['expected_output']
    # MetaClass = return_metaclass(meta_type)

    str_exr: list[str] = MetaClass._extract_str(d_n['content']) # type: ignore
    str_exr_true: list[str] = expected_output['str_extracted']
    
    if debug:
        return str_exr, str_exr_true
    assert_list_match(str_exr, str_exr_true)

def t__str_to_dict(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    inputs , expected_output, _ , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    meta_dict: dict = MetaClass._str_to_dict(inputs['str_extracted']) # type: ignore
    meta_dict_true: dict = expected_output['meta_dict']
    
    if debug:
        return meta_dict, meta_dict_true
    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_to_string(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    _ , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    m = MetaClass(d_n['content'])
    tostr: str = m.to_string() # type: ignore
    name_field_true: str = expected_output["field_name"]
    tostr_true: str = d_n[name_field_true]

    if debug:
        return tostr, tostr_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(tostr, tostr_true, msg=err_msg)

def t_update_content(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    _ , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)

    m = MetaClass(d_n['content'])
    upd: str = m.update_content(d_n['content']) # type: ignore
    name_field_true: str = expected_output["field_name"]
    upd_true: str = d_n[name_field_true]

    if debug:
        return upd, upd_true
    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(upd, upd_true, msg=err_msg)

def t_erase(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    _ , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    tostr: str = MetaClass.erase(d_n['content']) # type: ignore
    name_field_true: str = expected_output["field_name"]
    tostr_true: str = d_n[name_field_true]

    if debug:
        return tostr, tostr_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert_str_match(tostr, tostr_true, msg=err_msg)

def t_exists(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    _ , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    exists: bool = MetaClass.exists(d_n['content']) # type: ignore
    exists_true: str = expected_output['exists']

    if debug:
        return exists, exists_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert exists == exists_true, err_msg

def t_add(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    inputs , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    m = MetaClass(d_n['content'])
    m.add(k=inputs['k'], l=inputs['l'], overwrite=inputs['overwrite']) # type: ignore
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output['meta_dict']

    if debug:
        return meta_dict, meta_dict_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_remove(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    inputs , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    m = MetaClass(d_n['content'])
    m.remove(k=inputs['k'], l=inputs['l']) # type: ignore
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output['meta_dict']

    if debug:
        return meta_dict, meta_dict_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)

def t_remove_duplicate_values(test_id: str, data: dict, debug:bool=False) -> None:
 
    name_f = re.sub('^t_', '', inspect.currentframe().f_code.co_name)
    inputs , expected_output, d_n , d_t , MetaClass = prep_test_data(test_id, data, name_f)
    
    m = MetaClass(d_n['content'])
    m.remove_duplicate_values(k=inputs['k']) 
    meta_dict = m.metadata
    meta_dict_true: dict[str, list[str]] = expected_output['meta_dict']

    if debug:
        return meta_dict, meta_dict_true
    
    err_msg = build_error_msg(test_id, d_t)
    assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)



### TestTemplateMetadata   

def add_test_function_metadata(glob: dict, fn: TestTemplateMetadata, test_id: str, data: dict):
    ft = partial(fn, test_id=test_id, data=data)
    name_f = get_name_function_tested(fn)
    meta_type = get_test_meta_type(test_id=test_id, name_f=name_f, data=data)
    ft_name = f"test_{meta_type.value}_{name_f}_{test_id}"
    glob[ft_name] = ft

