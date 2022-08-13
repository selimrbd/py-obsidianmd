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

    def update_content(self, how_inline: str = "bottom"):
        self.content = self.metadata.update_content(self.content, how_inline=how_inline)

    def write(self, path: Union[Path, None] = None):
        """Write the current content to the note's path"""
        p = self.path if path is None else path
        with open(p, "w") as f:
            f.write(self.content)

    def sub(self, pattern: str, replace: str):
        self.content = re.sub(pattern, replace, self.content)

    def print(self):
        print(self.content)
