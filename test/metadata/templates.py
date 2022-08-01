import sys
from functools import partial
from typing import Callable

sys.path.append('../..')
from source.metadata import MetadataType, return_metaclass


def add_test_function_to_global(glob: dict, fn: Callable, note_name: str, data: dict, meta_type: MetadataType):
    ft = partial(fn, note_name=note_name, data=data, meta_type=meta_type)
    ft_name = f"test_{fn.__name__.split('_', maxsplit=1)[-1]}_{note_name}"
    glob[ft_name] = ft

def t_extract_str(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    
    with open(d['path'], 'r') as f:
        note_content = f.read()
    true_str_extracted = d[meta_type.value].get('str-extracted', list()) if meta_type.value in d else ''
    
    str_extracted = MetaClass._extract_str(note_content)

    if debug:
        return str_extracted, true_str_extracted

    assert (str_extracted == true_str_extracted)

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

    assert meta_dict == true_meta_dict

def t_build_metaobject(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])
    true_meta_dict = d[meta_type.value].get('metadata', dict()) if meta_type.value in d else dict()

    if debug:
        return mt, mt.metadata, true_meta_dict
    assert (mt.metadata == true_meta_dict)

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

    assert ( mt.to_string() == true_tostr )  

def t_add(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    if 'add-tests' not in d[meta_type.value]:
        return True

    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])

    add_tests = d[meta_type.value]['add-tests']
    
    if debug:
        return mt, d[meta_type.value]

    for tnum, ts in add_tests.items():
        mt = MetaClass(d['path'])
        mt.add(ts['k'], ts['v'], overwrite=ts['overwrite'])
        err_msg = f'add test failed: {tnum}. desc: {ts["desc"]}.\n'
        err_msg += f'output: {mt.metadata[ts["k"]]}\n'
        err_msg += f'expected result: {ts["result"]}\n'
        assert mt.metadata[ts['k']] == ts['result'], err_msg

def t_remove(note_name: str, data: dict, meta_type: MetadataType, debug:bool=False):
    d = data[note_name]
    if 'remove-tests' not in d[meta_type.value]:
        return True

    MetaClass = return_metaclass(meta_type)
    mt = MetaClass(d['path'])
    remove_tests = d[meta_type.value]['remove-tests']
    
    if debug:
        return mt, d[meta_type.value]

    for tnum, ts in remove_tests.items():
        mt = MetaClass(d['path'])
        mt.remove(ts['k'], ts['v'])
        err_msg = f'add test failed: {tnum}. desc: {ts["desc"]}.\n'
        err_msg += f'output: {mt.metadata.get(ts["k"], None)}\n'
        err_msg += f'expected result: {ts["result"]}\n'
        assert mt.metadata.get(ts["k"], None) == ts['result'], err_msg
