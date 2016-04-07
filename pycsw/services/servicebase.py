"""Base classes for pycsw services."""

import logging

from .. import utilities

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""
    _server = None

    _content_type_processors = None
    _kvp_processors = None

    def __init__(self, enabled):
        self.enabled = enabled
        self._server = None
        self._content_type_processors = utilities.ManagedList(
            manager=self, related_name="_service")
        self._kvp_processors = utilities.ManagedList(
            manager=self, related_name="_service")

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @property
    def server(self):
        """Return the server object that manages this service."""
        return self._server

    @property
    def content_type_processors(self):
        return self._content_type_processors

    @property
    def kvp_processors(self):
        return self._kvp_processors

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

    def get_schema_processor(self, request):
        """Get a suitable schema processor for the request

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.csw.cswbase.OgcSchemaProcessor
            The schema processor object that can process the request.

        """

        raise NotImplementedError


class RequestProcessor:
    namespaces = {}
    _schemas = None
    _service = None

    def __init__(self, namespaces=None):
        self.namespaces = namespaces.copy() or {}
        self._schemas = utilities.ManagedList(
            manager=self, related_name="_request_processor")
        self._service = None

    @property
    def service(self):
        return self._service

    @property
    def schemas(self):
        return self._schemas

    def get_schema_processor(self, request):
        """Get a suitable schema processor for the request

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.csw.cswbase.OgcSchemaProcessor
            The schema processor object that can process the request.

        """

        raise NotImplementedError


class SchemaProcessor:
    """Base class for implementing processors for specific schemas.

    This class serves a base for implementing processors for the various
    schemas that each service might accept. A SchemaProcessor is responsible
    for:

    * Parsing the incoming PycswHttpRequest object and extract general
      information from it. This allows the schema processor's parent, which is
      the generic request_processor, to decide which of its schema processors
      is able to process an input request
    * Parsing the incoming request and extract the relevant parameters for
      the requested operation. This means that each schema_parser must now
      which operations it is able to parse

    """
    namespace = ""
    _request_processor = None

    def __init__(self, namespace):
        self.namespace = namespace
        self._request_processor = None

    @property
    def request_processor(self):
        return self._request_processor

    def parse_general_request_info(self, request):
        """Extract general request information.

        This method analyses a request and extracts some general information
        from it.

        """
        raise NotImplementedError

    def process_request(self, request):
        raise NotImplementedError
