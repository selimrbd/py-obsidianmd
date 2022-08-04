from pathlib import Path

from source.metadata import MetadataType

from .a_tmp import (add_test_function_metadata, load_data, nmt_order,
                    nmt_order_keys, nmt_order_values,
                    nmt_remove_duplicate_values, parse_name_function_tested)

PATH_TEST_DEF = Path(__file__).parent/'test_NoteMetadata.json'
data = load_data(PATH_TEST_DEF)

for t_fn in [nmt_remove_duplicate_values, nmt_order_values, nmt_order_keys, nmt_order]:
    name_f = parse_name_function_tested(t_fn.__name__)
    test_ids: list[str] = list(data['tests'][f'tests-{name_f}'].keys())
    for tid in test_ids:
        add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data, meta_type=MetadataType.ALL)
