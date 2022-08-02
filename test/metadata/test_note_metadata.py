import sys

sys.path.append('../..')

from .. import load_test_data
from .templates import (nmt_add_test_function_to_global, nmt_erase,
                        nmt_remove_duplicate_values, nmt_update_content)

NOTE_NAMES = ["n4"]
DATA = load_test_data(NOTE_NAMES)

for fn in [nmt_remove_duplicate_values, nmt_erase, nmt_update_content]:
    for n in ["n4"]:
        nmt_add_test_function_to_global(glob=globals(), fn=fn, note_name=n, data=DATA)
