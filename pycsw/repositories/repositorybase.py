"""Repository base classes"""

import logging

from lxml import etree

from ..utilities import ManagedList
from .. import exceptions

logger = logging.getLogger(__name__)


class CswRepository:

    _typenames = None
    _query_translators = {}
    query_languages = None

    def __init__(self):
        self._typenames = ManagedList(manager=self, related_name="_repository")

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


