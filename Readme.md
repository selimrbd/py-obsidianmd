# py-obsidianmd

A python library for [ObsidianMD](https://obsidian.md/).

:warning: **Consider backing up your vault** before using the library, to avoid any risk of data loss.

## Features

**Modify your notes' metadata in batch:**
  - *Transfer metadata between frontmatter and inline ([dataview style](https://github.com/blacksmithgu/obsidian-dataview))*
  - Add and remove metadata fields
  - group all your inline metadata fields at the top/bottom of your notes
  - ...

## Quickstart

```bash
pip install py-obsidianmd
```

```python
from pathlib import Path
from pyomd import Notes
from pyomd.metadata import MetadataType

path_dir = Path('/path/to/obsidian/folder')
notes = Notes(path_dir)
```

### move metadata between frontmatter and inline

```python
notes.metadata.move(fr=MetadataType.FRONTMATTER, to=MetadataType.INLINE)
notes.update_content(inline_position="top", inline_tml="callout", inline_inplace=False) #type: ignore
notes.write()
```
![](./docs/imgs/pyomd-1.gif)

### regroup inline metadata inside a callout

```python
notes.update_content(inline_inplace=False, inline_position="top", inline_tml="callout") #type: ignore
notes.write()
```
![](./docs/imgs/pyomd-2.gif)

### add and remove metadata 
```python
notes.filter(has_meta=[("tags", "type/book", MetadataType.INLINE)])

notes.metadata.add(k="type", l="[[book]]", meta_type=MetadataType.INLINE)
notes.metadata.remove(k="tags", l="type/book", meta_type=MetadataType.INLINE)

notes.update_content(inline_inplace=False, inline_position="top", inline_tml="callout") #type: ignore
notes.write()
```
![](./docs/imgs/pyomd-3.gif)


## License

[BSD 3](LICENSE.txt)

## Contributing
Contributions are welcome ! Different ways you can contribute:
- **Write an issue**: report a bug, suggest an enhancement, ...
- **Submit a pull request** to solve an open issue

For more details, see the [contribution guidelines](CONTRIBUTING.md).

## Support
<WIP>
