"""Base classes for pycsw services."""

import logging

from .. import utilities

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""
    _server = None
    _operations = None

    _schema_processors = None

    def __init__(self):
        self._server = None
        self._schema_processors = utilities.ManagedList(
            manager=self, related_name="_service")
        self._operations = utilities.ManagedList(manager=self,
                                                 related_name="_service")

    def __repr__(self):
        return ("{0.__class__.__name__}(name={0.name!r}, "
                "version={0.version!r}, "
                "operations={0.operations!r}, "
                "schema_processors={0.schema_processors!r})".format(self))

    def __str__(self):
        return "{0.__class__.__name__}({0.identifier})".format(self)

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
    def schema_processors(self):
        """Return the available SchemaProcessor objects.

        SchemaProcessors are used to process requests.

        """
        return self._schema_processors

    @property
    def operations(self):
        """Return the available operations."""
        return self._operations

    def get_enabled_operation(self, name):
        """Return the operation that matches the input name.

        If an operation with a name that is euqla to the input name exists
        and is enabled it is returned.

        """

        for operation in (op for op in self.operations if op.enabled):
            if operation.name == name:
                result = operation
                break
        else:
            result = None
        return result

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
    _service = None
    namespaces = {}
    media_type = ""

    def __init__(self, namespaces=None, media_type=""):
        self.namespaces = namespaces.copy() if namespaces is not None else {}
        self._service = None

    @property
    def service(self):
        return self._service

    def parse_general_request_info(self, request):
        """Extract general request information.

        This method analyses a request and extracts some general information
        from it.

        """
        raise NotImplementedError

    def process_request(self, request):
        raise NotImplementedError
