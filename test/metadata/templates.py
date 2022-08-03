import inspect
import re
import sys
from functools import partial
from string import Template
from typing import Callable

import pytest

sys.path.append('../..')

from source.exceptions import ArgTypeError
from source.metadata import MetadataType, NoteMetadata, Order, return_metaclass


def add_test_function_to_global(glob: dict, fn: Callable, note_name: str, data: dict, meta_type: MetadataType|None=None):
    ft = partial(fn, note_name=note_name, data=data, meta_type=meta_type)
    ft_name = f"test_{fn.__name__.split('_', maxsplit=1)[-1]}_{note_name}"
    glob[ft_name] = ft

def nmt_add_test_function_to_global(glob: dict, fn: Callable, note_name: str, data: dict):
    ft = partial(fn, note_name=note_name, data=data)
    ft_name = f"test_{fn.__name__.split('_', maxsplit=1)[-1]}_{note_name}"
    glob[ft_name] = ft

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

def t_extract_str(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    
    with open(d['path'], 'r') as f:
        note_content = f.read()
    true_str_extracted = d[meta_type.value].get('str-extracted', list()) if meta_type.value in d else ''
    
    str_extracted = MetaClass._extract_str(note_content)

    if debug:
        return str_extracted, true_str_extracted

    assert_list_match(str_extracted, true_str_extracted)

def t_str_to_dict(note_name: str, data: dict, meta_type: MetadataType, debug: bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)

    if meta_type.value not in d:
        true_str_extracted = ''
        true_meta_dict = dict()
    else:
        true_str_extracted = d[meta_type.value].get('str-extracted', list())
        true_meta_dict = d[meta_type.value].get('metadata', dict())
    meta_dict = MetaClass._str_to_dict(true_str_extracted)

    if debug:
        return meta_dict, true_meta_dict

    assert_dict_match(meta_dict, true_meta_dict)

def t_build_metaobject(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])
    true_meta_dict = d[meta_type.value].get('metadata', dict()) if meta_type.value in d else dict()

    if debug:
        return mt, mt.metadata, true_meta_dict
    
    assert_dict_match(mt.metadata, true_meta_dict)

def t_exists(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    
    with open(d['path'], 'r') as f:
        content = f.read()
    true_meta_dict = d[meta_type.value].get('metadata', dict()) if meta_type.value in d else dict()

    if debug:
        return MetaClass, content, true_meta_dict

    assert ( MetaClass.exists(content) == (len(true_meta_dict) > 0) )    

def t_to_string(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    
    true_tostr = d[meta_type.value].get('tostr', '') if meta_type.value in d else ''
    mt = MetaClass(d['path'])
    
    if debug:
        return mt.to_string(), true_tostr

    assert_str_match(mt.to_string(), true_tostr)

def t_add(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]

    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])

    add_tests = d[meta_type.value]['add-tests']
    
    if debug:
        return mt, d[meta_type.value]

    for tnum, ts in add_tests.items():
        mt = MetaClass(d['path'])
        mt.add(ts['k'], ts['v'], overwrite=ts['overwrite'])
        err_msg = f'add test failed: {tnum}. desc: {ts["desc"]}.\n'
        assert_list_match(mt.metadata.get(ts["k"], None), ts['result'], msg=err_msg)

def t_remove(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]

    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])
    remove_tests = d[meta_type.value]['remove-tests']
    
    if debug:
        return mt, d[meta_type.value]

    for tnum, ts in remove_tests.items():
        mt = MetaClass(d['path'])
        mt.remove(ts['k'], ts['v'])
        err_msg = f'add test failed: {tnum}. desc: {ts["desc"]}.\n'
        assert_list_match(mt.metadata.get(ts["k"], None), ts['result'], msg=err_msg)

def t_remove_duplicate_values(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False) -> None:
    d = data[note_name]

    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])
    rdv_tests = d[meta_type.value].get('remove-duplicate-values-tests',dict())
    
    if debug:
        return mt, d[meta_type.value]

    for tnum, ts in rdv_tests.items():
        mt = MetaClass(d['path'])
        mt.remove_duplicate_values(ts['k'])
        err_msg = f'remove duplicate values test failed: {tnum}. desc: {ts["desc"]}.\n'
        assert_dict_match(mt.metadata, ts['result'], msg=err_msg)

def t_erase(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    with open(d['path'], 'r') as f:
        note_content = f.read()

    MetaClass = return_metaclass(meta_type)
    erased = MetaClass.erase(note_content)
    true_erased = d[meta_type.value].get('erase', '') if meta_type.value in d else ''
    
    if debug:
        return erased, true_erased

    assert_str_match(erased, true_erased)

def t_update_content(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False) -> None:
    
    d = data[note_name]
    with open(d['path'], 'r') as f:
        note_content = f.read()

    if debug:
        return d

    MetaClass = return_metaclass(meta_type)
    n = MetaClass(d['path'])
    upd_default = n.update_content(note_content)
    upd_default_true = d[meta_type.value].get('upd-default', '') if meta_type.value in d else ''

    assert_str_match(upd_default, upd_default_true)

def t_order_values(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    MetaClass = return_metaclass(meta_type)
    tests_ov = d[meta_type.value]['tests-order_values'] 

    for tnum, ts in tests_ov.items():
        m = MetaClass(d['path']) 
        arg_keys = ts["keys"]
        arg_how = eval(ts["how"]) if re.match("^Order\\.", ts["how"]) is not None else ts["how"]
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order_values(keys=arg_keys, how=arg_how)
        else:
            m.order_values(keys=arg_keys, how=arg_how) 
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}'
            assert_dict_match(m.metadata, res_true, msg=err_msg)

def t_order_keys(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    MetaClass = return_metaclass(meta_type)
    tests_okys = d[meta_type.value][f'tests-{fn_tested}'] 

    for tnum, ts in tests_okys.items():
        m = MetaClass(d['path'])
        arg_how = eval(ts["how"]) if re.match("^Order\\.", ts["how"]) is not None else ts["how"]
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order_keys(how=arg_how)
        else:
            m.order_keys(how=arg_how)
            list_keys = list(m.metadata.keys())
            list_keys_true = res_true
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}'
            err_msg += f'ORDER: {arg_how}, TYPE: {type(arg_how)}'
            assert_list_match(list_keys, list_keys_true, msg=err_msg)

def eval_arg_from_json(arg: str|None, re_match_pattern: str):
    if arg is None: return None
    try:
        if re.match(re_match_pattern, str(arg)) is not None: return eval(arg)
        return arg
    except AttributeError:
        return arg

def t_order(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    MetaClass = return_metaclass(meta_type)
    tests_order = d[meta_type.value][f'tests-{fn_tested}'] 

    for tnum, ts in tests_order.items():
        m = MetaClass(d['path'])
        arg_keys = ts["keys"]
        arg_o_keys = eval_arg_from_json(ts["o_keys"], re_match_pattern='^Order\\.')
        arg_o_values = eval_arg_from_json(ts["o_values"], re_match_pattern='^Order\\.')
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order(keys=arg_keys, o_keys=arg_o_keys, o_values=arg_o_values)
        else:
            m.order(keys=arg_keys, o_keys=arg_o_keys, o_values=arg_o_values)
            list_keys = list(m.metadata.keys())
            list_keys_true = res_true['list_keys']
            meta_dict = m.metadata
            meta_dict_true = res_true['metadata']
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}'
            err_msg += f'\nkeys: "{arg_keys}", o_keys: "{arg_o_keys}" ({type(arg_o_keys)}), o_values: "{arg_o_values}" ({type(arg_o_values)})'
            assert_list_match(list_keys, list_keys_true, msg=err_msg)
            assert_dict_match(meta_dict, meta_dict_true, msg=err_msg)
            


def nmt_remove_duplicate_values(note_name: str, data: dict, debug:bool=False) -> None:
    d = data[note_name]

    mt_all = NoteMetadata(d['path'])
    rdv_tests = d['notemeta']['remove-duplicate-values-tests']
    
    if debug:
        return mt, d['notemeta']

    for tnum, ts in rdv_tests.items():
        mt_all = NoteMetadata(d['path'])
        mt_all.remove_duplicate_values(k=ts['k'], meta_type=MetadataType.get_from_str(ts['meta_type']))
        err_msg = f'NOTEMETADATA - remove duplicate values test failed: {tnum}. desc: {ts["desc"]}.\n'
        err_msg += f"test values: (k=\"{ts['k']}\", meta type=\"{ts['meta_type']}\")\n"
        for t in ['frontmatter', 'inline']:
            err_msg += f'meta type: {t}\n'
            mt = getattr(mt_all, t)
            assert_dict_match(getattr(mt, 'metadata'), ts['result'][t], msg=err_msg)

def nmt_erase(note_name: str, data: dict, debug:bool=False) -> None:
    d = data[note_name]
    with open(d['path'], 'r') as f:
        note_content = f.read()

    erased_all = NoteMetadata.erase(note_content, meta_type=MetadataType.ALL)
    erased_all_true = d['notemeta']['eraseall']
    
    if debug:
        return erased_all, erased_all_true

    assert_str_match(erased_all, erased_all_true)

def nmt_update_content(note_name: str, data: dict, debug:bool=False) -> None:
    d = data[note_name]
    with open(d['path'], 'r') as f:
        note_content = f.read()

    nm = NoteMetadata(d['path'])
    upd_default = nm.update_content(note_content)
    upd_fm_only = nm.update_content(note_content, meta_type=MetadataType.FRONTMATTER)
    upd_inline_only = nm.update_content(note_content, meta_type=MetadataType.INLINE)
    upd_default_true = d['notemeta']['upd-default']
    upd_fm_only_true = d['frontmatter']['upd-default']
    upd_inline_only_true = d['inline']['upd-default']

    assert_str_match(upd_default, upd_default_true)
    assert_str_match(upd_fm_only, upd_fm_only_true)
    assert_str_match(upd_inline_only, upd_inline_only_true)

def nmt_order_values(note_name: str, data: dict, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    tests_ov = d['notemeta']['tests-order_values'] 

    for tnum, ts in tests_ov.items():
        m = NoteMetadata(d['path']) 
        arg_keys = ts["keys"]
        arg_how = eval(ts["how"]) if re.match("^Order\\.", ts["how"]) is not None else ts["how"]
        arg_meta_type = eval(ts["meta_type"]) if re.match("^MetadataType\\.", str(ts["meta_type"])) is not None else ts["meta_type"]
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order_values(keys=arg_keys, how=arg_how, meta_type=arg_meta_type)
        else:
            m.order_values(keys=arg_keys, how=arg_how, meta_type=arg_meta_type) 
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}'
            for typ in ['frontmatter', 'inline']:
                err_msg += f"\nmetadata type: {typ}"
                sub_meta = getattr(m, typ)
                dict_meta = getattr(sub_meta, 'metadata')
                dict_meta_true = res_true[typ]
                assert_dict_match(dict_meta, dict_meta_true, msg=err_msg)

def nmt_order_keys(note_name: str, data: dict, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    tests_oky = d['notemeta']['tests-order_keys'] 

    for tnum, ts in tests_oky.items():
        m = NoteMetadata(d['path']) 
        arg_how = eval(ts["how"]) if re.match("^Order\\.", ts["how"]) is not None else ts["how"]
        arg_meta_type = eval(ts["meta_type"]) if re.match("^MetadataType\\.", str(ts["meta_type"])) is not None else ts["meta_type"]
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order_keys(how=arg_how, meta_type=arg_meta_type)
        else:
            m.order_keys(how=arg_how, meta_type=arg_meta_type) 
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}\narg_how: "{arg_how}"\narg_meta_type: "{arg_meta_type}"\n'
            for typ in ['frontmatter', 'inline']:
                err_msg2 = err_msg+f"\nmetadata type: {typ}"
                sub_meta = getattr(m, typ)
                list_meta_keys = list(getattr(sub_meta, 'metadata').keys())
                list_meta_keys_true = res_true[typ]
                assert_list_match(list_meta_keys, list_meta_keys_true, msg=err_msg2)

def nmt_order(note_name: str, data: dict, debug:bool=False) -> None:
    
    fn_name = inspect.currentframe().f_code.co_name
    fn_tested = re.sub('^t_', '', fn_name)
    d = data[note_name] 
    tests_oky = d['notemeta']['tests-order'] 

    for tnum, ts in tests_oky.items():
        m = NoteMetadata(d['path']) 
        arg_keys = ts["keys"]
        arg_o_keys = eval_arg_from_json(ts["o_keys"], re_match_pattern='^Order\\.')
        arg_o_values = eval_arg_from_json(ts["o_values"], re_match_pattern='^Order\\.')
        arg_meta_type = eval_arg_from_json(ts["meta_type"], re_match_pattern="^MetadataType\\.")
        res_true = ts['result']
        if "RAISE_EXCEPTION" in res_true:
            exception_name = res_true["RAISE_EXCEPTION"]
            with pytest.raises(eval(exception_name)):
                m.order(keys=arg_keys, o_keys=arg_o_keys, o_values=arg_o_values, meta_type=arg_meta_type)
        else:
            m.order(keys=arg_keys, o_keys=arg_o_keys, o_values=arg_o_values, meta_type=arg_meta_type)
            err_msg = f'\n** "{fn_tested}" test failed **\ntest number: {tnum}\ndescription: {ts["desc"]}\n\narg_meta_type: "{arg_meta_type}"\n'
            for typ in ['frontmatter', 'inline']:
                err_msg2 = err_msg+f"\nmetadata type: {typ}"
                sub_meta = getattr(m, typ)
                list_meta_keys = list(getattr(sub_meta, 'metadata').keys())
                list_meta_keys_true = res_true[typ]['list_keys']
                meta_dict = sub_meta.metadata
                meta_dict_true = res_true[typ]['metadata']
                assert_list_match(list_meta_keys, list_meta_keys_true, msg=err_msg2)
                assert_dict_match(meta_dict, meta_dict_true, msg=err_msg2)

