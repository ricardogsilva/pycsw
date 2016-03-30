import importlib


def lazy_import_dependency(python_path, type_=None):
    the_module = importlib.import_module(python_path)
    result = the_module
    if type_ is not None:
        the_class = getattr(the_module, type_)
        result = the_class
    return result


class ManagedList:
    """A list where elements have a bidirectional relationship with a manager.

    This class is useful for managing objects that have a bidirectional
    relation with some other object that takes responsibility for managing
    them.
    """

    _data = None

    def __init__(self, manager=None, related_name=""):
        self._data = []
        self.related_name = related_name
        self.manager = manager

    def __iter__(self):  # making objects iterable
        return iter(self._data)

    def __getitem__(self, item):  # implementing the sequence protocol
        return self._data[item]

    def __len__(self):  # implementing the sequence protocol
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def __add__(self, other):
        return self._data + other._data

    def append(self, item):
        self._data.append(item)
        setattr(item, self.related_name, self.manager)

    def insert(self, index, item):
        self._data.insert(index, item)
        setattr(item, self.related_name, self.manager)

    def pop(self):
        item = self._data.pop()
        setattr(item, self.related_name, None)
        return item

    def remove(self, item):
        try:
            self._data.remove(item)
            setattr(item, self.related_name, None)
        except ValueError:
            raise

