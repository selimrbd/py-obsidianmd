import re
from pathlib import Path
from typing import Union

from pyomd.metadata import NoteMetadata


class Note:
    """Represents a note (text file in obsidian)
    - frontmatter: the note's frontmatter
    - body: the note's body (everything except the frontmatter)
    - content: frontmatter + body
    """

    def __init__(self, path: Union[Path, str]):
        self.path: Path = Path(path)
        with open(self.path, "r") as f:
            self.content: str = f.read()
        self.metadata: NoteMetadata = NoteMetadata(self.content)

    def __repr__(self) -> str:
        return f'Note (path: "{self.path}")\n'

    def update_content(self, inline_how: str = "bottom", inline_inplace: bool = True):
        self.content = self.metadata.update_content(
            self.content, inline_how=inline_how, inline_inplace=inline_inplace
        )

    def write(self, path: Union[Path, None] = None):
        """Write the current content to the note's path"""
        p = self.path if path is None else path
        with open(p, "w") as f:
            f.write(self.content)

    def sub(self, pattern: str, replace: str, is_regex: bool = False):
        if not is_regex:
            pattern = re.escape(pattern)
        self.content = re.sub(pattern, replace, self.content)

    def print(self):
        print(self.content)
