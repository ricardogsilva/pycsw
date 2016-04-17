"""Repository base classes.

A `CswRepository` object is associated with a service. It is the interface
between pycsw and concrete data repositories, whatever they may be (an ORM,
a CSV file, etc.). The repository is configured with the following information:

* What typenames it can query;
* The query languages that it can decode;
* The correspondence between pycsw's record classes and the internal properties
  of the data structures.

"""

import logging
import importlib.util
import os

from ..utilities import ManagedList
from .. import exceptions

logger = logging.getLogger(__name__)


class CswRepository:

    _typenames = None
    _query_translators = {}
    query_languages = None

    def __init__(self, extra_query_translator_modules=None):
        self._typenames = ManagedList(manager=self, related_name="_repository")
        if extra_query_translator_modules is not None:
            self.load_query_translators(extra_query_translator_modules)

    @classmethod
    def load_query_translators(cls, query_translator_modules):
        for module_path in query_translator_modules:
            name = os.path.splitext(os.path.basename(module_path))[0]
            spec = importlib.util.spec_from_file_location(name=name,
                                                          location=module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

    @property
    def typenames(self):
        return self._typenames

    def get_record_by_id(self, id):
        raise NotImplementedError

    def translate_query_elements(self, query, typenames):
        """Replace query elements with the names used internally.

        Query elements use publicly defined typenames and queryable properties.
        However, the underlying structure of the repository is private and
        follows its own naming and organisation schema. This method translates
        query elements between the public names and the private repository.

        """

        try:
            query_translator_func = self._query_translators[",".join(
                typenames)]
            translated_query = query_translator_func(query)
        except KeyError:
            raise exceptions.PycswError(
                "Typenames {} are not processable by "
                "repository {}".format(typenames, self)
            )
        return translated_query

    def execute_query(self, query, typenames=None):
        raise NotImplementedError



def query_translator(repository_class, *typenames):
    """A parametrized decorator to apply on query translator functions."""

    def decorate(func):
        repository_class._query_translators[",".join(typenames)] = func
        return func
    return decorate


