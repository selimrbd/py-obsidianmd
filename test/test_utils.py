import json
import os
from pathlib import Path
from typing import Union

PATH_TEST_DATA = Path(__file__).parent / "0-test-data"
PATH_TEST_NOTES = PATH_TEST_DATA / "notes"

from pyomd.metadata import MetadataType, Order


def load_test_notes(path_test_notes: Union[Path, None]) -> dict:
    """ """
    data = dict()
    if path_test_notes is None:
        return data
    note_dirs = os.listdir(path_test_notes)
    for nd in note_dirs:
        path_nd = path_test_notes / nd
        data[nd] = {"path": path_nd / f"{nd}.md"}
        with open(data[nd]["path"], "r") as f:
            data[nd]["content"] = f.read()
        md_files = [
            x
            for x in os.listdir(path_nd)
            if x.endswith(".md") and x != data[nd]["path"].name
        ]
        for mdf in md_files:
            path_mdf = path_nd / mdf
            field_name = Path(mdf).stem.split("-", maxsplit=1)[-1]
            with open(path_mdf, "r") as f:
                data[nd][field_name] = f.read()
    return data


def load_test_definitions(path_test_def: Path) -> dict:
    with open(path_test_def, "r") as f:
        test_def = json.load(f)
    return test_def


def load_data(
    path_test_def: Path, path_test_notes: Union[Path, None] = PATH_TEST_NOTES
) -> dict:
    data = load_test_notes(path_test_notes)
    data.update(load_test_definitions(path_test_def))
    return data


### parse arguments


def get_test_arg_meta_type(
    test_id: str, name_f: str, data: dict
) -> Union[MetadataType, str, None]:
    meta_type_str: str = data["tests"].get("default_meta_type", None)
    meta_type_str = data["tests"][f"tests-{name_f}"][test_id]["inputs"].get(
        "meta_type", meta_type_str
    )
    if meta_type_str is None:
        return None
    return parse_test_arg_meta_type(meta_type_str)


def parse_test_arg_meta_type(
    meta_type_str: Union[str, None]
) -> Union[MetadataType, str, None]:
    if meta_type_str == ">>MetadataType.FRONTMATTER":
        meta_type = MetadataType.FRONTMATTER
    elif meta_type_str == ">>MetadataType.INLINE":
        meta_type = MetadataType.INLINE
    elif meta_type_str == ">>MetadataType.ALL":
        meta_type = MetadataType.ALL
    else:
        meta_type = meta_type_str
    return meta_type


def parse_test_arg_order(order_str: str) -> Union[Order, str]:
    if order_str == ">>Order.ASC":
        order = Order.ASC
    elif order_str == ">>Order.DESC":
        order = Order.DESC
    else:
        order: Union[str, Order] = order_str
    return order


def parse_name_function_tested(name_f: str):
    return name_f.split("_", maxsplit=1)[-1]
