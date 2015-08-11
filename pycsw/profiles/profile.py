"""
Base implementation for pycsw profiles
"""

import logging


LOGGER = logging.getLogger(__name__)


class Profile(object):
    name = ""
    typenames = []
    elementsetnames = []
    outputformats = dict()
    outputschemas = dict()
    namespaces = dict()
    properties = []
    additional_operations = []

    def deserialize_record(self, raw_record):
        """Convert a request into the pycsw representation

        :arg raw_record: The input record
        :type raw_record: str
        :return: The deserialized record
        :rtype: pycsw.core.models.Record
        """
        raise NotImplementedError

    def serialize_record(self, record, outputschema=None,
                         elementsetname=None, outputformat=None):
        """
        Convert pycsw's representation of a record into the suitable format

        :arg record: The record instance to serialize
        :type record: pycsw.core.models.Record
        :return: The serialized record
        :rtype: str
        """
        raise NotImplementedError

    def extend_get_capabilities(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_describe_record(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_get_records(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_get_record_by_id(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_get_domain(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_transaction(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass

    def extend_harvest(self, *args, **kwargs):
        """Reimplement in derived classes to provide extra functionality"""
        pass
