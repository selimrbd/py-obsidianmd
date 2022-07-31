import json
import sys
from pathlib import Path

sys.path.append('..')
from source.note import Frontmatter, Note

PATH_M1 = Path('test/test-data/m1.md')
PATH_M2 = Path('test/test-data/m2.md')
PATH_M3 = Path('test/test-data/m3.md')

def test_has_frontmatter_m1():
    n = Note(PATH_M1)
    assert not Frontmatter.has_frontmatter(n)
    
def test_has_frontmatter_m2():
    n = Note(PATH_M2)
    assert Frontmatter.has_frontmatter(n)

def test_has_frontmatter_m3():
    n = Note(PATH_M3)
    assert not Frontmatter.has_frontmatter(n)

def test_get_frontmatter_str_m1():
    n = Note(PATH_M1)
    str = Frontmatter._extract_str(n.content)[0]
    assert len(str) == 0

def test_get_frontmatter_str_m2():
    n = Note(PATH_M2)
    path_res = PATH_M2.parent/f'{PATH_M2.stem}-frontmatter.md'
    with open(path_res, 'r') as f:
        res = f.read()
    str = Frontmatter._extract_str(n.content)[0]
    assert str == res

def test_get_frontmatter_str_m3():
    n = Note(PATH_M3)
    str = Frontmatter._extract_str(n.content)[0]
    assert len(str) == 0

def test_build_frontmatter_m1():
    n = Note(PATH_M1)
    f = Frontmatter(n.content)
    assert len(f.metadata) == 0

def test_build_frontmatter_m2():
    n = Note(PATH_M2)
    f = Frontmatter(n.content)
    path_fm_dict = PATH_M2.parent/f'{PATH_M2.stem}-metadata_f.json'
    with open(path_fm_dict, 'r') as file:
        fm_dict = json.load(file)
    assert (f.metadata == fm_dict)

def test_build_frontmatter_m3():
    n = Note(PATH_M3)
    f = Frontmatter(n.content)
    assert len(f.metadata) == 0

def test_to_string_m1():
    n = Note(PATH_M1)
    f = Frontmatter(n.content)
    assert f.to_string() is None

def test_to_string_m2():
    n = Note(PATH_M2)
    f = Frontmatter(n.content)
    path_fm_str = PATH_M2.parent/f'{PATH_M2.stem}-frontmatter-tostr.md'
    with open(path_fm_str, 'r') as file:
        fm_str = file.read()
    assert f.to_string() == fm_str

def test_add_m2():
    n = Note(PATH_M2)
    f = Frontmatter(n.content)
    path_fm_dict = PATH_M2.parent/f'{PATH_M2.stem}-metadata_f.json'
    with open(path_fm_dict, 'r') as file:
        fm_dict = json.load(file)
    f.add('tags', 't4')
    fm_dict["tags"].append('t4')
    assert f.metadata == fm_dict

    f.add('meta2', [3,4])
    fm_dict["meta2"] += ["3", "4"]
    assert f.metadata == fm_dict

    f.add('newmeta', 'val')
    fm_dict["newmeta"] = ["val"]
    assert f.metadata == fm_dict

    f.add('meta2', [3,4], overwrite=True)
    assert f.metadata['meta2'] == ["3", "4"]


def test_remove_m2():
    n = Note(PATH_M2)
    f = Frontmatter(n.content)

    f.remove('tags')
    assert 'tags' not in f.metadata

    f.remove('meta2',2)
    assert f.metadata["meta2"] == ["1", "3"]

    f.remove('meta3',["foo","b bar"])
    assert f.metadata["meta3"] == list()
