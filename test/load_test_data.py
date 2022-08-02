import json
import os
import sys
from pathlib import Path

sys.path.append('..')
from source.metadata import MetadataType

PATH_TESTDATA = Path('test/0-test-data')

def load_test_data(note_names: list[str]) -> dict:
    ## setup data
    data: dict = dict()
    for c in note_names:
        path_note_dir = PATH_TESTDATA/c
        data[c] = {'path': path_note_dir/f'{c}.md'}
        ## load metadata file
        path_meta = PATH_TESTDATA/f'{c}/{c}-meta.json'
        if not path_meta.exists():
            raise ValueError(f'file "{path_meta}" does not exist.')
        with open(path_meta, 'r') as f:
            meta = json.load(f)
        for meta_type in [MetadataType.INLINE.value, MetadataType.FRONTMATTER.value, MetadataType.ALL.value]: 
            data[c][meta_type] = meta.get(meta_type, dict())
        
        ## load md files
        md_files = [x for x in os.listdir(path_note_dir) if x.endswith('.md') and x != f'{c}.md']
        print('md files:')
        print(md_files)
        for mdf in md_files:
            path_file = path_note_dir/mdf
            file_name = Path(mdf).stem
            meta_type = file_name.split('-')[1]
            property = file_name.split('-', maxsplit=2)[2]
            if path_file.exists():
                with open(path_file, 'r') as f:
                    data[c][meta_type][property] = f.read()
    
    return data
