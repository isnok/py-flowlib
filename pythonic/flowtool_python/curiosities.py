class AttrDict(dict):
    """ A hacky way to create a dict with it's keys accessible as attributes.
        Can cause memory leaks on old python versions.

        TODO: find the stackoverflow again where this is from...

        >>> d = AttrDict({'foo': 'bar'}, bar='baz')
        >>> len(d)
        2
    """

    def __init__(self, *args, **kwd):
        dict.__init__(self, *args, **kwd)
        self.update(self.__dict__)
        self.__dict__ = self


