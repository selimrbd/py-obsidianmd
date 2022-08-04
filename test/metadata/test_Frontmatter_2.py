from pathlib import Path

from .a_tmp import (add_test_function_metadata, load_data,
                    parse_name_function_tested, t__extract_str, t__str_to_dict,
                    t_erase, t_exists, t_to_string, t_update_content)

PATH_TEST_DEF = Path(__file__).parent/'test_Frontmatter.json'
data = load_data(PATH_TEST_DEF)

for t_fn in [t__extract_str, t__str_to_dict, t_to_string, t_update_content, t_exists, t_erase]:
    name_f = parse_name_function_tested(t_fn.__name__)
    test_ids: list[str] = list(data['tests'][f'tests-{name_f}'].keys())
    for tid in test_ids:
        add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data)
