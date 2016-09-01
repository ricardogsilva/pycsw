"""Base classes for pycsw services.

A service has:

* RequestParsers, which are used to parse the request
* Operations, which take care of actually processing the request
* ResponseRenderers, that generate the output format requested by the client

"""

import logging

from .. import utilities
from .. import exceptions

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    title = ""
    url_path = ""  # used for building URLs for the service
    abstract = ""
    keywords = None
    fees = ""
    access_constraints = ""
    namespaces = {}

    _name = ""
    _version = ""
    _server = None
    _operations = None

    _request_parsers = None
    _response_renderers = None


    def __init__(self, title="", abstract="", keywords=None, fees="",
                 access_constraints="", namespaces=None):
        self.title = title
        self.abstract = abstract
        self.keywords = list(keywords) if keywords is not None else []
        self.fees = fees
        self.access_constraints = access_constraints
        self.namespaces = dict(namespaces) if namespaces is not None else {}
        self._server = None
        self._request_parsers = utilities.ManagedList(
            manager=self, related_name="_service")
        self._response_renderers = utilities.ManagedList(
            manager=self, related_name="_service")
        self._operations = utilities.ManagedList(manager=self,
                                                 related_name="_service")

    def __repr__(self):
        return ("{0.__class__.__name__}(name={0.name!r}, "
                "version={0.version!r}, "
                "operations={0.operations!r}, "
                "request_parsers={0.request_parsers!r})".format(self))

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
    def request_parsers(self):
        """Return the available RequestParser objects."""
        return self._request_parsers

    @property
    def response_renderers(self):
        """Return the available ResponseRenderer objects."""
        return self._response_renderers

    @property
    def operations(self):
        """Return the available operations."""
        return self._operations

    @property
    def default_output_format(self):
        possible = "text/xml"
        if possible in [r.output_format for r in self.response_renderers]:
            result = possible
        else:  # lets get the first media type
            for r in self.response_renderers:
                if r.output_format is not None:
                    result = r.output_format
                    break
            else:  # could not get a default media type
                result = None
        return result


    def get_enabled_operation(self, name):
        """Return the operation that matches the input name.

        If an operation with a name that is equal to the input name exists
        and is enabled it is returned.

        """

        for operation in (op for op in self.operations if op.enabled):
            if operation.name == name:
                result = operation
                break
        else:
            raise exceptions.PycswError("Operation {!r} is not "
                                        "enabled".format(name))
        return result

    def get_request_parser(self, request):
        """Get a suitable RequestParser object for the request

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        RequestParser
            The request_parser object that can process the request.

        """

        raise NotImplementedError

    def get_renderer(self, operation, request):
        """Get a suitable renderer for the requested operation.

        Parameters
        ----------
        operation: pycsw.services.csw.operations.operationbase.CswOperation
            The operation that was requested.
        request: pycsw.httprequest.PycswHttpRequest
            The original request
        """
        raise NotImplementedError

    def get_urls(self):
        """Get the URLs for the operations defined in the service.

        """

        raise NotImplementedError


class RequestParser:
    """Base class for implementing parsers for specific schemas.

    This class serves a base for implementing parsers for the various
    schemas that each service might accept. A RequestParser is responsible
    for:

    * Parsing the incoming PycswHttpRequest object and extract general
      information from it. This allows the parser's parent, which is
      the underlying service, to decide which of its RequestParsers
      is able to process an input request
    * Parsing the incoming request and extract the relevant parameters for
      the requested operation. This means that each reuqest_parser must know
      which operations it is able to parse

    """

    _service = None
    namespaces = {}
    media_type = ""

    def __init__(self):
        self._service = None

    def __str__(self):
        return "{0.__class__.__name__}(media_type={0.media_type!r})".format(
            self)

    @property
    def service(self):
        return self._service

    def parse_general_request_info(self, request):
        """Extract general request information.

        This method analyses a request and extracts some general information
        from it.

        """

        raise NotImplementedError

    def parse_request(self, request):
        raise NotImplementedError


class ResponseRenderer:
    _service = None
    output_format = None
    output_schema = None

    def __init__(self):
        self._service = None

    def __repr__(self):
        return ("{0.__class__.__name__}(output_format={0.output_format!r}, "
                "output_schema={0.output_schema!r})".format(self))

    def __str__(self):
        return ("{0.__class__.__name__}({0.output_format}, "
                "{0.output_schema})".format(self))

    @property
    def service(self):
        return self._service

    def render(self, response):
        raise NotImplementedError

    def can_render(self, operation, request):
        raise NotImplementedError
