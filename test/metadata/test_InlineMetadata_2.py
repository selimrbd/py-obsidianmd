from pathlib import Path

from source.metadata import MetadataType

from .a_tmp import (add_test_function_metadata, get_name_function_tested,
                    load_data, t__extract_str, t__str_to_dict)

PATH_TEST_DEF = Path(__file__).parent/'test_InlineMetadata.json'
META_TYPE = MetadataType.INLINE
data = load_data(PATH_TEST_DEF)

for t_fn in [t__extract_str, t__str_to_dict]:
    name_f = get_name_function_tested(t_fn)
    test_ids: list[str] = list(data['tests'][f'tests-{name_f}'].keys())
    for tid in test_ids:
        add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data, meta_type=META_TYPE)
