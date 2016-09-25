import importlib
import logging

logger = logging.getLogger(__name__)


def lazy_import_dependency(python_path, type_=None):
    the_module = importlib.import_module(python_path)
    result = the_module
    if type_ is not None:
        the_class = getattr(the_module, type_)
        result = the_class
    return result


def query_translator(repository_class_path, *typenames):
    """A parametrized decorator to apply on query translator functions."""

    def decorate(func):
        module_path, class_name = repository_class_path.rsplit(".", maxsplit=1)
        repository_class = lazy_import_dependency(module_path,
                                                  type_=class_name)
        repository_class._query_translators[",".join(typenames)] = func
        return func
    return decorate


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


class LazyList:
    """A container that loads its instances only when they are needed.

    This is a specialized class that should be used instead of a normal Python
    list whenever there is a need to store instances of classes that might
    not be all used at runtime. An example application is the list of
    RequestParser objects that a pycsw Service class supports. A CSW 2.0.2
    service may support parsing requests in multiple formats. However,
    during normal WSGI runtime, the server will operate on a single request
    at a time. Therefore it may not be necessary to load all RequestParsers.
    The same happens with a Service's Operation classes.

    Parameters
    ----------
    contents: list
        A list with the items that are to be instantiated lazily. Two types of
        lists are valid:

        * A list of strings where each string is the python class path to the
          class that is to be instantiated;

        * A list of two-element tuples, where the first element of the tuple
          is the class path and the second element is a dictionary with
          keyword arguments to use when instantiating the class

    Examples
    --------

    This first example shows the usage of the first form of the ``contents``
    input argument

    >>> first_list = LazyList([
    ...     "pycsw.services.csw.cswbase.CswOgcSchemaProcessor"])

    The second example shows the usage of the second form of the ``contents``
    input argument

    >>> second_list = LazyList([
    ...     ("pycsw.services.csw.cswbase.CswOgcKvpProcessor",
    ...      {"my_constraint": 2})
    ... ])

    """

    def __init__(self, contents=None):
        contents = contents or []
        self._contents = list(contents)

    def __iter__(self):  # makes objects iterable
        for item in self._contents:
            yield self._instantiate_item(item)

    def __getitem__(self, position):  # implementing the sequence protocol
        return self._instantiate_item(self._contents[position])

    def __len__(self):  # part of the sequence protocol
        return len(self._contents)

    def __repr__(self):
        return repr(self._contents)

    def __add__(self, other):
        return self.__class__(self._contents + other._contents)

    def append(self, item):
        self._contents.append(item)

    def insert(self, index, item):
        self._contents.insert(index, item)

    def pop(self):
        return self._contents.pop()

    def remove(self, item):
        self._contents.remove(item)

    def _instantiate_item(self, item):
        index = self._contents.index(item)
        if isinstance(item, str):
            logger.debug("Loading {0!r}...".format(item))
            module_path, class_name = item.rpartition(".")[::2]
            ImportedClass = lazy_import_dependency(
                module_path, class_name)
            instance = ImportedClass()
            self._contents[index] = instance
        else:
            try:
                class_path, init_kwargs = list(iter(item))
                logger.debug("Loading {0!r} with {1!r}...".format(
                    class_path, init_kwargs))
            except TypeError:  # index is not iterable
                instance = item
            else:
                module_path, class_name = class_path.rpartition(".")[::2]
                ImportedClass = lazy_import_dependency(
                    module_path, class_name)
                instance = ImportedClass(**init_kwargs)
                self._contents[index] = instance
        return instance


class LazyManagedList(LazyList):

    def __init__(self, contents=None, manager=None, related_name=""):
        super().__init__(contents=contents)
        self.related_name = related_name
        self.manager = manager

    def append(self, item):
        self._contents.append(item)
        self._setup_bidirectional_relationship(item)

    def insert(self, index, item):
        self._contents.insert(index, item)
        self._setup_bidirectional_relationship(item)

    def pop(self):
        item = self._contents.pop()
        try:
            setattr(item, self.related_name, None)
        except AttributeError:
            pass
        return item

    def remove(self, item):
        try:
            self._contents.remove(item)
            setattr(item, self.related_name, None)
        except ValueError:
            raise
        except AttributeError:
            pass

    def _instantiate_item(self, item):
        instance = super()._instantiate_item(item)
        setattr(instance, self.related_name, self.manager)
        return instance

    def _setup_bidirectional_relationship(self, item):
        try:
            # if we are inserting an object, set up the bidirectional relation
            setattr(item, self.related_name, self.manager)
        except AttributeError:
            # set up the bidirectional relationship later
            pass

