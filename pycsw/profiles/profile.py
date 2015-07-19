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
    mandatory_queryables = dict()
    additional_queryables = dict()
    mandatory_returnables = dict()
    additional_returnables = dict()
    namespaces = dict()

    def __init__(self):
        self.add_properties()

    def add_property(self, property, queryable=True, returnable=True,
                      mandatory=True, elementsetnames=None):
        """Add a property to the profile

        :param property:
        :param queryable:
        :param returnable:
        :param mandatory:
        :return:
        """
        elementsetnames = elementsetnames or ["all"]
        if queryable:
            if mandatory:
                self.mandatory_queryables[property.name] = property
            else:
                self.additional_queryables[property.name] = property
        if returnable:
            if mandatory:
                self.mandatory_returnables[property.name] = (property,
                                                             elementsetnames)
            else:
                self.additional_returnables[property.name] = (property,
                                                              elementsetnames)

    def add_properties(self):
        """Add profile queryables and returnables

        This method must be reimplemented in child classes
        """
        raise NotImplementedError

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
