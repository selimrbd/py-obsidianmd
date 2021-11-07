Python utilities for the personal knowledge management tool [Obsidian](https://obsidian.md/)


## Motivation

I wanted to modify my notes' metadata in batch and couldn't find an existing plugin to do so.
If some of the functionalities you see here are already available in a plugin, please let me know.
Open for contributions.

## Basic usage


```{python}
path = Path('path/to/file')
note = Note(path)

## print frontmatter
print(note.frontmatter)

## get the note's metadata (from frontmatter) as a dict
note.metadata

## get list of tags
print(note.tags)

## add a tag
note.add_tag('tag_name')

## remove a tag
note.remove_tag('tag_name')

## write the note with the updated metadata
note.write()
```

Original motivation: add a tag to all files in a folder

```{python}
import os
from pathlib import Path
from source.note import Note

path_dir = Path('path/to/dir')

for r,d,fls in os.walk(path_dir):
    for f in fls:
        pth = Path(r)/f
        note = Note(pth)
        note.add_tag('tag_name')
        note.write()
```
