from functools import partial
from typing import Callable

TestTemplateNote = Callable[[str, dict, MetadataType, bool], None]


def add_test_function_metadata(
    glob: dict,
    fn: TestTemplateMetadata,
    test_id: str,
    data: dict,
    meta_type: Union[MetadataType, None] = None,
):

    ft = partial(fn, test_id=test_id, data=data)
    name_f = parse_name_function_tested(fn.__name__)
    if meta_type is None:
        meta_type = get_test_arg_meta_type(test_id=test_id, name_f=name_f, data=data)
    ft_name = f"test_{meta_type.value}_{name_f}_{test_id}"
    glob[ft_name] = ft
