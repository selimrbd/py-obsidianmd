from curses import meta
from pathlib import Path

from source.metadata import MetadataType

from .a_tmp import (add_test_function_metadata, get_name_function_tested,
                    load_data, nmt_remove_duplicate_values)

PATH_TEST_DEF = Path(__file__).parent/'test_NoteMetadata.json'
data = load_data(PATH_TEST_DEF)

for t_fn in [nmt_remove_duplicate_values]:
    name_f = get_name_function_tested(t_fn)
    test_ids: list[str] = list(data['tests'][f'tests-{name_f}'].keys())
    for tid in test_ids:
        add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data, meta_type=MetadataType.ALL)
