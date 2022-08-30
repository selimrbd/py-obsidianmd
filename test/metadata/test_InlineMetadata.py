from pathlib import Path

from ..test_utils import load_data
from .templates import (
    add_test_function_metadata,
    parse_name_function_tested,
    t_erase,
    t_exists,
    t_parse,
    t_remove_and_update,
    t_to_string,
    t_update_content,
)


def main():
    PATH_TEST_DEF = Path(__file__).parent / "test_InlineMetadata.json"
    data = load_data(PATH_TEST_DEF)

    for t_fn in [
        t_parse,
        t_to_string,
        t_update_content,
        t_exists,
        t_erase,
        t_remove_and_update,
    ]:
        name_f = parse_name_function_tested(t_fn.__name__)
        test_ids: list[str] = list(data["tests"][f"tests-{name_f}"].keys())
        for tid in test_ids:
            add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data)


main()
