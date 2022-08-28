# py-obsidianmd

A python library for [ObsidianMD](https://obsidian.md/).

Currently focused on enabling obsidian users to **experiment between different ways of organizing their notes metadata**. See the [full reference here](https://selimrbd.github.io/py-obsidianmd/)

<br>

:warning: so far the library has been tested on very few different vaults. **Consider backing up your vault** or committing it to git before testing it, to avoid any risk of data loss.

## Introduction video

<WIP>

## Features
- add and remove metadata fields in batch
- move metadata between the frontmatter and inline ([dataview](https://github.com/blacksmithgu/obsidian-dataview) style)
- group all your inline metadata fields at the top/bottom of your notes
- order your metadata fields and values: sort alphabetically, remove duplicates, ...

## Quickstart

### installation
Install the library using pip:
```zsh
pip install py-obsidianmd
```

### example vault
You can test the libraries functionalities on an example vault, "example-pkb" provided in this repository (examples/vaults/example-pkb). Here are some of the operations you can do:

### Add metadata to a group of notes

```python
from pyomd import Notes
from pyomd.metadata import MetadataType
from pathlib import Path

path_dir = Path('my-knowledge-base')

# create a "Notes" object. Filter to keep only notes having the "type/book" tag
nts = Notes(paths=[path_dir]).filter(has_meta={'tags': 'type/book'})

# add a new inline metadata field "up" and assign the value of "[[NOTETYPE - Book]]" 
nts.metadata.add(k='parent', values=["[[NOTETYPE - Book]]"], meta_type=MetadataType.INLINE)

# update the notes content and write them to disk
nts.update_content(write=True)
```

For a step-by-step example, see [the introduction video](#introduction-video).
For a list of all the libraries' feature, see the [full reference](https://selimrbd.github.io/py-obsidianmd/)

## License

[BSD 3](LICENSE.txt)

## Contributing
Contributions are more than welcome. Different ways you can contribute:
- **Write an issue**: report a bug, suggest an enhancement, ...
- **Submit a pull request** to solve an open issue

For more details, see the [contribution guidelines](CONTRIBUTING.md).

## Support
<WIP>