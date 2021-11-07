from __future__ import annotations
from dataclasses import dataclass, field
import re
from pathlib import Path



REGEX_FRONTMATTER = '(?s)(^---\n).*?(\n---\n)'

class Note:
    """Represents a note (text file in obsidian)
    - frontmatter: the note's frontmatter
    - body: the note's body (everything except the frontmatter)
    - content: frontmatter + body
    """
    def __init__(self, path: Path|str):
        self.path = Path(path)
        self.content = self.read_content()
        self.frontmatter = Frontmatter.extract_frontmatter(self.content)
        self.body = self.read_body()
        
    @property
    def tags(self):
        """The note's tags (only those present in the frontmatter)"""
        return self.frontmatter.tags        

    def __repr__(self) -> str:
         return f"file path: {self.path}" + "\n" + f"{self.frontmatter.__repr__()}"
        
    def read_content(self) -> str:
        """Opens the file and reads it's content"""
        with open(self.path, 'r') as f:
            return f.read()
        
    def read_body(self) -> str:
        """Get's the note body by removing the frontmatter from the content"""
        return re.sub(REGEX_FRONTMATTER, '', self.content)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the note's frontmatter"""
        self.frontmatter.add_tag(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Removes a tag from the note's frontmatter"""
        self.frontmatter.remove_tag(tag)
        
    def update_content(self):
        """Updates the note content"""
        self.content = f"{self.frontmatter.to_string()}{self.body}"
        
    def to_string(self):
        """Renders the note as a string"""
        self.update_content()
        return self.content
    
    def write(self):
        """Write the current content to the note's path"""
        with open(self.path, 'w') as f:
            f.write(self.to_string())
    
@dataclass
class Frontmatter:
    """Represents the frontmatter of a note"""
    yaml_str: str = None
    metadata: dict = field(default_factory=lambda: dict(tags=list()))
        
    def __repr__(self):
        if self.yaml_str is None:
            return 'Metadata: None'
        return 'Metadata:\n' + ''.join([f'- {k}: {v}\n' for k,v in self.metadata.items()])
        
    @property
    def tags(self):
        """List containing the note's tags present in the frontmatter"""
        if self.metadata is None:
            return list()
        return self.metadata.get('tags', list())
    
    @staticmethod
    def extract_frontmatter(content: str) -> Frontmatter:
        """Extracts the frontmatter from the note's content"""
        mtc = re.search(REGEX_FRONTMATTER, content)
        if mtc is None:
            return Frontmatter()
        yaml_str = re.sub('---\n', '', mtc.group())
        metadata = Frontmatter.yaml_str_to_dict(yaml_str)
        return Frontmatter(yaml_str=yaml_str, metadata=metadata)
        
    @staticmethod
    def yaml_str_to_dict(s: str) -> dict:
        """Reads the yaml frontmatter information (string) and transforms it into a dictionary"""
        x = re.sub('---', '', s)
        x = x.split('\n')
        metadata = {}
        for e in x:
            if ':' not in e: continue
            k,v  = e.split(':', maxsplit=1)
            metadata[k.strip()] = v.strip()
            
        ## read tags metadata
        if 'tags' in metadata:
            tags = [t.strip() for t in metadata['tags'].split(' ') if t.strip() != '']
            metadata['tags'] = tags
        else:
            metadata['tags'] = list()
        return metadata
    
    @staticmethod
    def has_frontmatter(content: str) -> bool:
        """Checks if a frontmatter is present in the content"""
        return re.search(REGEX_FRONTMATTER, content) is not None
    
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
            
    def update_yaml_str(self):
        """generates a string from self.metadata"""
        metadata_repr = [f"{k}: {v}\n" for k,v in self.metadata.items() if k != 'tags']
        
        ## add tag metadata
        repr_tag = 'tags: '
        if len(self.tags) > 0:
            repr_tag += " ".join(self.tags)
        metadata_repr.append(repr_tag)
        self.yaml_str = '---\n' + ''.join(metadata_repr)+ '\n---\n'
        
    def to_string(self):
        """Generates a string representation of the frontmatter"""
        self.update_yaml_str()
        return self.yaml_str