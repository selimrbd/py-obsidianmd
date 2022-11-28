# py-obsidianmd

A python library for [ObsidianMD](https://obsidian.md/) for modifying your notes in batch.

:warning: **Consider backing up your vault** before using the library, to avoid any risk of data loss.


## Presentation video

[![Watch the video](https://img.youtube.com/vi/CzmDQyxJS88/hqdefault.jpg)](https://www.youtube.com/watch?v=CzmDQyxJS88)

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

You can test the library on this [example vault](https://github.com/selimrbd/example-vault)

## move metadata between frontmatter and inline

```python
notes.metadata.move(fr=MetadataType.FRONTMATTER, to=MetadataType.INLINE)
notes.update_content(inline_position="top", inline_tml="callout", inline_inplace=False) #type: ignore
notes.write()
```
![](./docs/imgs/pyomd-1.gif)

## regroup inline metadata inside a callout

```python
notes.update_content(inline_inplace=False, inline_position="top", inline_tml="callout") #type: ignore
notes.write()
```
![](./docs/imgs/pyomd-2.gif)

## add and remove metadata 
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
<a href="https://www.paypal.com/donate/?hosted_button_id=R5NYTS46CQMSS"><img src="./docs/imgs/donate-paypal.png" width="150" height="100" /></a>
<br>
<a href="https://ko-fi.com/selimrbd"><img src="./docs/imgs/support-kofi.png" width="200" height="50" /></a>