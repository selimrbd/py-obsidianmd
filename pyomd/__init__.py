#import pkg_resources
import sys

if sys.version_info >= (3,8):
    from importlib import metadata as metadata_object
else:
    import importlib_metadata as metadata_object

from .config import Config
from .note import Note, Notes

#version = pkg_resources.get_distribution("py-obsidianmd").version
version = metadata_object.version('py-obsidianmd')

_ = Config
_ = Note
_ = Notes
