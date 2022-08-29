from pathlib import Path

import hydra
from pyomd.metadata import MetadataType

from ..test_utils import load_data
from .templates import (
    add_test_function_metadata,
    nmt_get,
    nmt_has,
    nmt_move,
    nmt_order,
    nmt_order_keys,
    nmt_order_values,
    nmt_remove_duplicate_values,
    nmt_update_content,
    parse_name_function_tested,
)


def main():
    PATH_TEST_DEF = Path(__file__).parent / "test_NoteMetadata.json"
    data = load_data(PATH_TEST_DEF)

    for t_fn in [
        nmt_remove_duplicate_values,
        nmt_order_values,
        nmt_order_keys,
        nmt_order,
        nmt_move,
        nmt_update_content,
        nmt_has,
        nmt_get,
    ]:
        name_f = parse_name_function_tested(t_fn.__name__)
        test_ids: list[str] = list(data["tests"][f"tests-{name_f}"].keys())
        for tid in test_ids:
            add_test_function_metadata(
                glob=globals(),
                fn=t_fn,
                test_id=tid,
                data=data,
                meta_type=MetadataType.ALL,
            )


main()
