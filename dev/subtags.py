    # @staticmethod
    # def _get_subtags(tag: str) -> list[str]:
    #     """get list of al subtags of a tag"""
    #     sp = tag.split('/')
    #     return ['/'.join(sp[0:(i+1)]) for i in range(len(sp))]
    
    # def has_tag(self, tag: str) -> bool:
    #     """Returns true if the tag or one of its children is in the frontmatter, false otherwise
    #     Ex:
    #         - frontmatter has tag "type/source/video"
    #         - tag="type/source" --> returns True
    #     """
    #     return any([tag in Frontmatter.get_subtags(t) for t in self.tags])
