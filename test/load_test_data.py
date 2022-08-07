import json
import os
from pathlib import Path

PATH_TEST_DATA = Path(__file__).parent/'0-test-data'
PATH_TEST_NOTES = PATH_TEST_DATA/'notes'


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
