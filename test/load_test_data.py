import json
import sys
from pathlib import Path
from typing import Union

sys.path.append('..')
from source.metadata import MetadataType

PATH_TESTDATA = Path('test/0-test-data')
MD_FILES = ["frontmatter-tostr", "inline-tostr", "inline-erase", "frontmatter-erase", "notemeta-erase"]

def load_test_data(note_names: list[str], md_files: list[str] = MD_FILES) -> dict:
    ## setup data
    data: dict = dict()
    for c in note_names:
        data[c] = {'path': PATH_TESTDATA/f'{c}/{c}.md'}
        ## load metadata file
        path_meta = PATH_TESTDATA/f'{c}/{c}-meta.json'
        if not path_meta.exists():
            raise ValueError(f'file "{path_meta}" does not exist.')
        with open(path_meta, 'r') as f:
            meta = json.load(f)
        for meta_type in [MetadataType.INLINE.value, MetadataType.FRONTMATTER.value, MetadataType.ALL.value]: 
            data[c][meta_type] = meta.get(meta_type, dict())
        
        ## load md files
        for mdf in md_files:
            path_file = PATH_TESTDATA/f'{c}/{c}-{mdf}.md'
            meta_type = mdf.split('-')[0]
            property = mdf.split('-')[1]
            # if not path_file.exists():
            #     raise ValueError(f'file "{path_file}" does not exist.')
            if path_file.exists():
                with open(path_file, 'r') as f:
                    data[c][meta_type][property] = f.read()
    
    return data
