from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum
from pathlib import Path
from typing import Optional, OrderedDict, Type, Union

from .exceptions import ArgTypeError

UserInput = Union[str,int,float]
MetaDict = dict[str, list[str]]

class Order(Enum):
    ASC = "asc"
    DESC = "desc"

class Metadata(ABC):

    REGEX: str = ''

    def __init__(self, path: Path|str):
        with open(path, 'r') as f:
            note_content = f.read()
        self.metadata: MetaDict = self._extract_metadata(note_content)
    
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
    def to_string(self) -> str:
        """Render metadata as a string.
        
        If repr is True, print to screen
        """
        pass

    @abstractmethod
    def update_content(self, note_content: str) -> str:
        ...

    def _extract_metadata(self, note_content: str) -> MetaDict:
        meta_str = self._extract_str(note_content)
        return self._str_to_dict(meta_str)

    @classmethod
    def exists(cls, note_content: str) -> bool:
        """Checks if the metadata type is present in the note"""
        return re.search(cls.REGEX, note_content) is not None

    @classmethod
    def erase(cls, note_content: str) -> str:
        return re.sub(cls.REGEX, '', note_content)

    def add(self, k: str, l: Union[UserInput, list[UserInput], None], overwrite: bool=False) -> None:
        """adds a metadata field, or new values if it already exists
        
        If overwrite is set to True, the old value is overwritten. Otherwise, new elements are
        appended.
        """
        if l is None: 
            nl = list()
        elif isinstance(l, UserInput):
            nl = [str(l)]
        else:
            nl = [str(x) for x in l]
        
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
        if len(self.metadata[k]) == 0:
            del self.metadata[k]

    def remove_duplicate_values(self, k: str|list[str]|None=None) -> None:

        if k is None:
            list_keys = list(self.metadata.keys())
        elif isinstance(k, str):
            list_keys = [k]
        elif isinstance(k, list):
            list_keys = k
        else:
            raise ArgTypeError('k', type(k), str(Optional[str|list[str]]))
        
        for k2 in list_keys:
            if k2 not in self.metadata: continue
            self.metadata[k2] = list(dict.fromkeys(self.metadata[k2]))

    def print(self):
        print(self.to_string())

    def order_values(self, keys: str|list[str]|None=None, how: Order=Order.ASC) -> None:
        """Orders metadata values.
        
        Attributes:
            - k: key on which to order the values. If None, orders all values
        """
        if not isinstance(how, Order): raise ArgTypeError('how', type(how), Order) # type: ignore
        
        if keys is None: keys = list(self.metadata.keys())
        if isinstance(keys, str): keys = [keys]
        for k in keys:
            reverse = False if (how == Order.ASC) else True
            self.metadata[k] = sorted(self.metadata[k], reverse=reverse)
    
    def order_keys(self, how: Order=Order.ASC) -> None:
        """Orders metadata keys.

        Utilizes that since 3.6, python dict remember insert order.
        """
        reverse = (how == Order.DESC)
        list_keys = sorted(list(self.metadata.keys()),reverse=reverse)
        self.metadata = {k:self.metadata.pop(k) for k in list_keys}
        
    def order(self, keys: str|list[str]|None=None, o_keys: Order|None=Order.ASC, o_values: Order|None=Order.ASC):
        """Orders metadata keys and values.
        
        Attributes:
            - keys: keys for which to order the values
            - o_keys: how to order the keys. If None, don't order them
            - o_values: how to order values. If None, don't order them
        """
        if o_keys is not None:
            self.order_keys(how=o_keys)
        if o_values is not None:
            self.order_values(keys=keys, how=o_values)
        return None

class Frontmatter(Metadata):
    """Represents the frontmatter of a note"""

    REGEX = '(?s)(^---\n).*?(\n---\n)'

    @staticmethod
    def _extract_str(note_content: str) -> list[str]:
        """Returns the frontmatter detect as a string. (Empty string if not found)"""
        mtc = re.search(Frontmatter.REGEX, note_content)
        if mtc is None: return []
        fm_str = mtc.group()
        return [fm_str]      

    @staticmethod
    def _str_to_dict(meta_str: list[str]) -> MetaDict:
        """Reads the yaml frontmatter information (string) and transforms it into a dictionary"""
        metadata: MetaDict = {}
        if len(meta_str) == 0: return {}
        ms = meta_str[0]
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
    
    def to_string(self) -> str:
        """Render metadata as a string.
        
        If repr is True, print to screen
        """
        if len(self.metadata) == 0: return ''
        metadata_repr = [f"{k}: {', '.join(v)}\n" for k,v in self.metadata.items()]
        out = '---\n' + ''.join(metadata_repr)+ '---\n'
        return out

    def update_content(self, note_content: str) -> str:
        """
        """
        res = self.erase(note_content)
        res = self.to_string() + res
        return res

class InlineMetadata(Metadata):
    """Represents the inline metadata of a note"""

    REGEX = '[A-z]\w+ ?::.*'

    @staticmethod
    def _extract_str(note_content: str) -> list[str]:
        return re.findall(InlineMetadata.REGEX, note_content)

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

    def to_string(self) -> str:
        """Render metadata as a string.
        
        If repr is True, print to screen
        """
        if len(self.metadata) == 0: return ''
        r = "\n\n---\n- **@ metadata:**\n"
        for k,v in self.metadata.items(): r += f"    - {k}:: {', '.join(v)}\n"
        return r

    def update_content(self, note_content: str) -> str:
        """
        """
        res = self.erase(note_content)
        res = res + self.to_string()
        return res

class MetadataType(Enum):
    FRONTMATTER = 'frontmatter'
    INLINE = 'inline'
    ALL = 'notemeta'

    @staticmethod
    def get_from_str(s: str|None) -> MetadataType:
        if s is None: return MetadataType.ALL
        for k in MetadataType:
            if s == k.value: return k
        raise ValueError(f'Metadatatype not defined: "{s}"')

class NoteMetadata:
    """Represents all a note's metadata (frontmatter, inline and body tags)."""
    def __init__(self, path: Path|str):
        self.path = Path(path)
        self.frontmatter = Frontmatter(path)
        self.inline = InlineMetadata(path)
        #self.bodytags = BodyTags(path)
    
    @classmethod
    def _parse_arg_meta_type(cls, meta_type: MetadataType|None) -> MetadataType:
        if meta_type is None: meta_type = MetadataType.ALL
        if not isinstance(meta_type, MetadataType): #type: ignore
                raise ArgTypeError(var_name='meta_type', given_type=type(meta_type), 
                expected_type=str(MetadataType|None))
        return meta_type

    def remove_duplicate_values(self, k: str|list[str]|None, meta_type: MetadataType|None=None):
        """Remove duplicate values in the note's metadata
        
        Attributes:
            - k: key or list of keys on which to perform the duplication removal. If None, do on all keys
            - meta_type: target Metadata type. If None, does it on all metadata
        """
        meta_type = self._parse_arg_meta_type(meta_type) 
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.remove_duplicate_values(k=k)
        elif meta_type == MetadataType.INLINE:
            self.inline.remove_duplicate_values(k=k)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.remove_duplicate_values(k=k)
            self.inline.remove_duplicate_values(k=k)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')

    @classmethod
    def erase(cls, note_content: str, meta_type: MetadataType|None) -> str:
        """Erase metadata from note content
        
        Arguments:
            - note_content: string representing a note's content 
            - meta_type: if None, erases all metadata
        """
        meta_type = cls._parse_arg_meta_type(meta_type)
        res = note_content
        if meta_type == MetadataType.FRONTMATTER:
            res = Frontmatter.erase(res)
        elif meta_type == MetadataType.INLINE:
            res = InlineMetadata.erase(res)
        elif meta_type == MetadataType.ALL:
            res = Frontmatter.erase(res)
            res = InlineMetadata.erase(res)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')
        return res

    def update_content(self, note_content: str, meta_type: MetadataType|None=None) -> str:
        meta_type = self._parse_arg_meta_type(meta_type)
        res = note_content
        if meta_type == MetadataType.FRONTMATTER:
            res = self.frontmatter.update_content(res)
        elif meta_type == MetadataType.INLINE:
            res = self.inline.update_content(res)
        elif meta_type == MetadataType.ALL:
            res = self.frontmatter.update_content(res)
            res = self.inline.update_content(res)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')
        return res

    def order_values(self, keys: str|list[str]|None=None, how: Order=Order.ASC, meta_type: MetadataType|None=None) -> None:
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order_values(keys=keys, how=how)
        elif meta_type == MetadataType.INLINE:
            self.inline.order_values(keys=keys, how=how)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order_values(keys=keys, how=how)
            self.inline.order_values(keys=keys, how=how)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')
        
    def order_keys(self, how: Order=Order.DESC, meta_type: MetadataType|None=None) -> None:
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order_keys(how=how)
        elif meta_type == MetadataType.INLINE:
            self.inline.order_keys(how=how)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order_keys(how=how)
            self.inline.order_keys(how=how)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')
    
    def order(self, keys: str|list[str]|None=None, o_keys: Order|None=Order.ASC, o_values: Order|None=Order.ASC, meta_type: MetadataType|None=None):
        meta_type = self._parse_arg_meta_type(meta_type)
        if meta_type == MetadataType.FRONTMATTER:
            self.frontmatter.order(keys=keys, o_keys=o_keys, o_values=o_values)
        elif meta_type == MetadataType.INLINE:
            self.inline.order(keys=keys, o_keys=o_keys, o_values=o_values)
        elif meta_type == MetadataType.ALL:
            self.frontmatter.order(keys=keys, o_keys=o_keys, o_values=o_values)
            self.inline.order(keys=keys, o_keys=o_keys, o_values=o_values)
        else:
            raise ValueError(f'Unsupported value for argument meta_type: {meta_type}')
    

def return_metaclass(meta_type: MetadataType) -> Type[Metadata]:
    if meta_type == MetadataType.FRONTMATTER:
        return Frontmatter
    elif meta_type == MetadataType.INLINE:
        return InlineMetadata
    else:
        raise NotImplementedError(f'no metadata class implemented of type "{meta_type}"')
