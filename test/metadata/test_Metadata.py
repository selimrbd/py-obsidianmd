from pathlib import Path

from ..test_utils import load_data
from .templates import (
    add_test_function_metadata,
    parse_name_function_tested,
    t_add,
    t_order,
    t_order_keys,
    t_order_values,
    t_remove,
    t_remove_duplicate_values,
)


def main():
    PATH_TEST_DEF = Path(__file__).parent / "test_Metadata.json"
    data = load_data(PATH_TEST_DEF)

    for t_fn in [
        t_add,
        t_remove,
        t_remove_duplicate_values,
        t_order_values,
        t_order_keys,
        t_order,
    ]:
        name_f = parse_name_function_tested(t_fn.__name__)
        test_ids: list[str] = list(data["tests"][f"tests-{name_f}"].keys())
        for tid in test_ids:
            add_test_function_metadata(glob=globals(), fn=t_fn, test_id=tid, data=data)


main()
