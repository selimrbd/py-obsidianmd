import unittest
from pathlib import Path
from source.note import Note
import os

PATH_NOTE1 = Path('test/test-data/note1.md')


class TestTagsOperations(unittest.TestCase):
    """Series of unit test regarding tag manipulation"""
    
    def setUp(self):
        self.path = PATH_NOTE1
        self.path_tmp = self.path.parent/(f'{self.path.stem}-modif.md')
        assert self.path.exists(), f'{self.path} does not exist'
        
    def tearDown(self) -> None:
        if self.path_tmp.exists():
            os.remove(self.path_tmp)
    
    def test_note_creation(self):
        n = Note(self.path)
    
    def test_read_tags(self):
        n = Note(self.path)
        self.assertEqual(n.tags, ['tag1', 'tag2', 'tag3'])
        
    def test_add_a_tag(self):
        n = Note(self.path)
        n.add_tag('tag4')
        n.path = self.path_tmp
        n.write()
        n = Note(self.path_tmp)
        print(f'THE TAGS: {n.tags}')
        self.assertListEqual(n.tags, ['tag1', 'tag2', 'tag3', 'tag4'])
    
    def test_remove_a_tag(self):
        n = Note(self.path)
        n.remove_tag('tag3')
        n.path = self.path_tmp
        n.write()
        n = Note(self.path_tmp)
        print(f'THE TAGS: {n.tags}')
        self.assertListEqual(n.tags, ['tag1', 'tag2'])