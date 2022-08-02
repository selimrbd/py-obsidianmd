import sys

sys.path.append('../..')
from source.metadata import MetadataType

from .. import load_test_data
from .templates import (add_test_function_to_global, t_add, t_build_metaobject,
                        t_erase, t_exists, t_extract_str, t_remove,
                        t_remove_duplicate_values, t_str_to_dict, t_to_string)

META_TYPE = MetadataType.FRONTMATTER
NOTE_NAMES = ["n1", "n2", "n3", "n4", "n6"]
DATA = load_test_data(NOTE_NAMES)


for fn in [t_build_metaobject, t_extract_str, t_str_to_dict, t_exists, t_to_string]:
    for n in NOTE_NAMES:
        add_test_function_to_global(glob=globals(), fn=fn, note_name=n, data=DATA, meta_type=META_TYPE)

nl = ['n2']
for fn in [t_add, t_remove]:
    for n in nl:
        add_test_function_to_global(glob=globals(), fn=fn, note_name=n, data=DATA, meta_type=META_TYPE)

nl = ['n4']
for fn in [t_remove_duplicate_values, t_erase]:
    for n in nl:
        add_test_function_to_global(glob=globals(), fn=fn, note_name=n, data=DATA, meta_type=META_TYPE)
