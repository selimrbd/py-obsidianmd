from pathlib import Path

from source.metadata import NoteMetadata


class Note:
    """Represents a note (text file in obsidian)
    - frontmatter: the note's frontmatter
    - body: the note's body (everything except the frontmatter)
    - content: frontmatter + body
    """
    def __init__(self, path: Path|str):
        self.path: Path = Path(path)
        with open(self.path, 'r') as f:
            self.content: str = f.read()
        self.metadata: NoteMetadata = NoteMetadata(self.content)

    def __repr__(self) -> str:
         return f'Note (path: "{self.path}")\n'

    def update_content(self):
        self.content = self.metadata.update_content(self.content)

    def write(self):
        """Write the current content to the note's path"""
        with open(self.path, 'w') as f:
            f.write(self.content)

    def print(self):
        print(self.content)
