#from __future__ import annotations

import re
import statistics
from abc import ABC, abstractmethod, abstractstaticmethod
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from pathlib import Path
from typing import Optional, Tuple, Union

UserInput = Union[str,int,float]
MetaDict = dict[str, list[str]]

class Note:
    """Represents a note (text file in obsidian)
    - frontmatter: the note's frontmatter
    - body: the note's body (everything except the frontmatter)
    - content: frontmatter + body
    """
    def __init__(self, path: Path|str):
        self.path = Path(path)
        self.content = self._read_content()
        #self.frontmatter = Frontmatter.extract(self.content)
        #self.inline_metadata = InlineMetadata.extract_inline_metadata(self.content)
        #self.body = self._read_body()
        self.metadata_f = None #metadata in the frontmatter
        self.metadata_i = None #inline metadata
        self.metadata_b = None #metadata in the body (only tags)

    def __repr__(self) -> str:
         return f"file path: {self.path}" + "\n" + f"{self.frontmatter.__repr__()}"

    @property
    def metadata(self) -> dict[str, list[str]]:
        """Returns all metadata (from body, inline and frontmatter)"""
        ...
    
    def get_f_metadata(self) -> dict[str, Tuple[list[str], str]]:
        """The note's metadata (from the frontmatter)"""   
        return self.frontmatter.metadata
    
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

    def _read_content(self) -> str:
        """Opens the file and reads it's content"""
        with open(self.path, 'r') as f:
            return f.read()
        
    def _read_body(self) -> str:
        """Get's the note body by removing the frontmatter from the content"""
        return re.sub(REGEX_FRONTMATTER, '', self.content)

    def update_content(self):
        """Updates the note content"""
        self.content = f"{self.frontmatter.to_string()}{self.body}"

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

    
@dataclass
class Metadata(ABC):

    metadata: MetaDict
    
    def __repr__(self):
        r = f"metadata of type {type(self)}:\n"
        if self.to_string() is None:
             r +=' None'
        else:
            r += ''.join([f'- {k}: {", ".join(v)}\n' for k,v in self.metadata.items()])
        return r

    @staticmethod
    @abstractmethod
    def _extract_str(note_content: str) -> list[str]:
        pass

    @staticmethod
    @abstractmethod
    def _str_to_dict(meta_str: list[str]) -> MetaDict:
        pass
  
    @abstractmethod
    def to_string(self) -> Optional[str]:
        pass

    def _extract_metadata(self, note_content: str) -> MetaDict:
        meta_str = self._extract_str(note_content)
        return self._str_to_dict(meta_str)

    def add(self, k: str, l: Union[UserInput, list[UserInput]], overwrite: bool=False) -> None:
        """adds a metadata field, or new values if it already exists
        
        If overwrite is set to True, the old value is overwritten. Otherwise, new elements are
        appended.
        """
        nl = [str(l)] if isinstance(l, UserInput) else [str(x) for x in l]
        if overwrite:
            self.metadata[k] = nl
        else:
            if k in self.metadata:
                self.metadata[k] += nl
            else:
                self.metadata[k] = nl        

    def remove(self, k: str, l: Optional[Union[UserInput, list[UserInput]]]=None) -> None:
        """removes a metadata field"""
        if k not in self.metadata:
            return 
        if l is None:
            del self.metadata[k]
            return
        nl = [str(l)] if isinstance(l, UserInput) else [str(x) for x in l]
        self.metadata[k] = [e for e in self.metadata[k] if e not in nl]

    def remove_duplicates(self, k: str) -> None:
        ...

class Frontmatter(Metadata):
    """Represents the frontmatter of a note"""
    REGEX_FRONTMATTER = '(?s)(^---\n).*?(\n---\n)'

    def __init__(self, note_content: str):
        self.metadata: MetaDict = self._extract_metadata(note_content)

    @staticmethod
    def has_frontmatter(note: Note) -> bool:
        """Checks if a frontmatter is present in the content"""
        return re.search(Frontmatter.REGEX_FRONTMATTER, note.content) is not None

    @staticmethod
    def _extract_str(note_content: str) -> list[str]:
        """Returns the frontmatter detect as a string. (Empty string if not found)"""
        mtc = re.search(Frontmatter.REGEX_FRONTMATTER, note_content)
        if mtc is None: return ['']
        fm_str = mtc.group()
        return [fm_str]      

    @staticmethod
    def _str_to_dict(meta_str: list[str]) -> MetaDict:
        """Reads the yaml frontmatter information (string) and transforms it into a dictionary"""
        metadata: MetaDict = {}
        ms = meta_str[0]
        if len(ms) == 0: return {}
        elements = ms.split('\n')
        for e in elements:
            if ':' not in e: continue
            k,v  = e.split(':', maxsplit=1)
            c = [v.strip()] if ',' not in v else [x.strip() for x in v.split(',')]
            metadata[k.strip()] = c
        if 'tags' in metadata:
            mtags = ' '.join(metadata['tags'])
            metadata['tags'] = [t.strip() for t in mtags.split(' ') if t.strip() != '']
        return metadata
        
    def to_string(self) -> Optional[str]:
        """Generates a string representation of the frontmatter"""
        if len(self.metadata) == 0: return None
        metadata_repr = [f"{k}: {', '.join(v)}\n" for k,v in self.metadata.items()]
        out = '---\n' + ''.join(metadata_repr)+ '---\n'
        return out


class InlineMetadata(Metadata):
    """Represents the inline metadata of a note"""

    REGEX_INLINE_META = '[A-z]\w+ ?::.*'
    def __init__(self, note_content: str):
        self.metadata: MetaDict = self._extract_metadata(note_content)

    @staticmethod
    def _extract_str(note_content: str) -> list[str]:
        return re.findall(InlineMetadata.REGEX_INLINE_META, note_content)

    @staticmethod
    def _str_to_dict(meta_str: list[str]) -> MetaDict:
        metadata: MetaDict = dict()
        tmp: dict[str, str] = dict()
        for x in meta_str:
            k, v = x.split('::')[0].strip(), x.split('::')[1].strip()
            if k not in tmp:
                tmp[k] = v
            else:
                tmp[k] += f', {v}' 
        metadata = {k:[x.strip() for x in v.split(',')] for (k,v) in tmp.items()}
        if 'tags' in metadata:
            mtags = ' '.join(metadata['tags'])
            metadata['tags'] = [t.strip() for t in mtags.split(' ') if t.strip() != '']
        return metadata

    def to_string(self) -> Optional[str]:
        if len(self.metadata) == 0: return None
        r = "# metadata\n"
        for k,v in self.metadata.items(): r += f"- {k}:: {', '.join(v)}\n"
        return r

