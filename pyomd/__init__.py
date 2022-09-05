import pkg_resources

from .config import Config
from .note import Note, Notes

version = pkg_resources.get_distribution("py-obsidianmd").version

_ = Config
_ = Note
_ = Notes
