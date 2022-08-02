from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple, Union

UserInput = Union[str,int,float]
MetaDict = dict[str, list[str]]

from source.metadata import Frontmatter, InlineMetadata


class Note:
    """Represents a note (text file in obsidian)
    - frontmatter: the note's frontmatter
    - body: the note's body (everything except the frontmatter)
    - content: frontmatter + body
    """
    def __init__(self, path: Path|str):
        self.path = Path(path)
        self.content = self._read_content()
        self.frontmatter = Frontmatter(path)
        self.inline_meta = InlineMetadata(path)

    def __repr__(self) -> str:
         return f"file path: {self.path}" + "\n" + f"{self.frontmatter.__repr__()}"
    
    def _read_content(self) -> str:
        """Opens the file and reads it's content"""
        with open(self.path, 'r') as f:
            return f.read()
    
    def to_string(self):
        """Renders the note as a string"""
        self.update_content()
        return self.content
    
    def write(self):
        """Write the current content to the note's path"""
        with open(self.path, 'w') as f:
            f.write(self.to_string())

    def print(self):
        print(self.content)

    def sub(self, old: str, new: str) -> None:
        self.body = re.sub(old, new, self.body)
        self.update_content()


    @property
    def tags(self):
        """The note's tags (only those present in the frontmatter)"""
        return self.metadata.get('tags', list())

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note's frontmatter"""
        self.frontmatter.add_tag(tag)

    def has_tag(self, tag: str) -> bool:
        """Returns true if the tag or one of its children is in the frontmatter, false otherwise
        Ex:
            - frontmatter has tag "type/source/video"
            - tag="type/source" --> returns True
        """
        return any([tag in Frontmatter.get_subtags(t) for t in self.tags])
    
    @staticmethod
    def get_subtags(tag: str) -> list[str]:
        """get list of al subtags of a tag"""
        sp = tag.split('/')
        return ['/'.join(sp[0:(i+1)]) for i in range(len(sp))]
    
    def has_exact_tag(self, tag: str) -> bool:
        """Returns true if the exact tag is in the frontmatter, False otherwise"""
        return tag in self.tags
    
    def add_tag(self, tag: str) -> None:
        """Adds tag to the frontmatter
        TODO: check that the tag or a parent doesn't already exist
        """
        if self.metadata is None:
            return 
        if self.has_exact_tag(tag):
            return
        self.metadata['tags'].append(tag)

    def remove_tag(self, tag: str) -> None:
        if self.has_exact_tag(tag):
            self.tags.remove(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Removes a tag from the note's frontmatter"""
        self.frontmatter.remove_tag(tag)
