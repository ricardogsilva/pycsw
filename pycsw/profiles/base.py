"""
Base implementation for pycsw profiles

Since pycsw implements the HTTP protocol binding, all profiles must use this
protocol binding as well.
"""

from __future__ import absolute_import
import logging

from ..core.etree import etree


GET_CAPABILITIES = "GetCapabilities"
DESCRIBE_RECORD = "DescribeRecord"
GET_DOMAIN = "Getdomain"
GET_RECORD_BY_ID = "GetRecordById"
GET_RECORDS = "GetRecords"
TRANSACTION = "Transaction"
HARVEST = "Harvest"


LOGGER = logging.getLogger(__name__)


class BaseProfile(object):
    """Base profile for pycsw.

    All profiles must derive from this class and implement the relevant
    interface.
    """

    name = ""
    """A descriptive name for the profile."""

    version = ""
    """A version for the profile."""

    typenames = []
    """An iterable with the qualified names of the profile's types."""

    elementsetnames = []
    """An iterable with the names of predefined element result sets that the
    profile may specify."""

    outputformats = dict()
    """A mapping with the name of each output format as key and its
    Internet media type of the format as value."""

    outputschemas = dict()  #: key: name, value: schema namespace
    """A mapping with the name of each output schema as key and its namespace
    as value."""

    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "ogc": "http://www.opengis.net/ogc",
    }  #: Extend this to add more namespaces than csw and ogc
    """A mapping with the prefix of each namespace as key and its full
    description as value. Extend this to add more namespaces than the
    normative 'csw' and 'ogc' ones."""

    properties = []
    """Populate this list with instances of
       `pycsw.config.properties.CswProperty` defining the queryables and
    returnables of each profile."""

    operations = dict()
    """A mapping with the name of each operation as key and the method used
    for processing it as value. Use the `establish_operations` method to
    modify this variable indirectly."""

    def __init__(self):
        self.establish_operations()

    def establish_operations(self):
        """
        Establish a profile's operations

        The general CSWT operations for HTTP are:

        * GetCapabilities
        * DescribeRecord
        * Getdomain
        * GetRecordById
        * GetRecords
        * Transaction
        * Harvest

        Extend this method in custom profiles if there is a need to add more
        operations besides the ones defined in the HTTP protocol binding of
        CSW's general catalogue model. Otherwise this method does not need to
        be overriden.

        :return:
        """
        self.operations[GET_CAPABILITIES] = self.execute_get_capabilities
        self.operations[DESCRIBE_RECORD] = self.execute_describe_record
        self.operations[GET_DOMAIN] = self.execute_get_domain
        self.operations[GET_RECORD_BY_ID] = self.execute_get_record_by_id
        self.operations[GET_RECORDS] = self.execute_get_records
        self.operations[TRANSACTION] = self.execute_transaction
        self.operations[HARVEST] = self.execute_harvest

    def deserialize_record(self, raw_record):
        """
        Convert a record to its internal representation.

        The internal representation of a record is as an instance of
        `pycsw.core.models.Record`. The input record representation is
        dependant on each profile. However, the CSW standard mandates that
        there shall always be a schema from which it is possible to establish
        mappings that allow retrieving the core common properties from a
        record. These mappings should be used here.

        :param raw_record:
        :return:
        """

        raise NotImplementedError

    def serialize_record(self, record, output_format=None, output_schema=None,
                         element_set_name=None, element_names=None):
        """
        Convert a record to the desired format and schema.

        :param record:
        :param format:
        :param schema:
        :param elementsetname:
        :param elementnames:
        :return:
        """

        raise NotImplementedError

    def execute_operation(self, name, *operation_args, **operation_kwargs):
        """
        A wrapper for the execution of profile operations.

        Use this method instead of calling each of the operations directly.
        This makes it possible to add new, profile dependent operations and
        still use the same interface for their execution.

        :param name:
        :param operation_args:
        :param operation_kwargs:
        :return:
        """
        operation = self.operations[name]
        result = operation(*operation_args, **operation_kwargs)
        return result

    def execute_get_capabilities(self, request):
        """Reimplement this method in custom profiles

        At this point, we assume the server has already validated the
        'service', 'version' and 'request' parameters.

        :arg request: The pre-processed request
        :type request: dict
        """
        # sections, accept_versions, accept_formats, update_sequence
        raise NotImplementedError

    def execute_describe_record(self, *args, **kwargs):
        """Reimplement this method in custom profiles"""
        raise NotImplementedError

    def execute_get_domain(self, *args, **kwargs):
        """Reimplement this method in custom profiles"""
        raise NotImplementedError

    def execute_get_record_by_id(self, repository, identifier,
                                 output_format=None, output_schema=None,
                                 element_set_name=None, element_names=None):
        """Perform the CSW GetRecordById operation.

        Reimplement this method in custom profiles if needed.

        :arg repository:
        :type repository:
        :arg identifier:
        :type identifier:
        :returns:
        :rtype:
        """

        record = repository.query_ids(identifier).scalar()
        LOGGER.debug("record: {}".format(record))
        result = ""
        if record is not None:
            result = self.serialize_record(record, output_format=output_format,
                                           output_schema=output_schema,
                                           element_set_name=element_set_name,
                                           element_names=element_names)
        return result

    def execute_get_records(self, *args, **kwargs):
        """Reimplement this method in custom profiles"""
        raise NotImplementedError

    def execute_transaction(self, *args, **kwargs):
        """Reimplement this method in custom profiles"""
        raise NotImplementedError

    def execute_harvest(self, *args, **kwargs):
        """Reimplement this method in custom profiles"""
        raise NotImplementedError

    @staticmethod
    def _parse_to_element_tree(raw_record):
        if not isinstance(raw_record, etree._Element):
            try:
                # FIXME: harden this XML parsing or move it out of here
                exml = etree.parse(raw_record)
            except Exception:
                raise
        else:
            exml = raw_record
        return exml
