import logging

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""
    _server = None

    def __init__(self, enabled, server=None):
        self.enabled = enabled
        self._server = server

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @property
    def server(self):
        """Return the server object that manages this service."""
        return self._server

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

    def accepts_request(self, request):
        """Find out if the incoming request can be processed by this service.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.csw.cswbase.CswSchemaProcessor
            The schema processor object that can process the request.

        """

        raise NotImplementedError


class RequestProcessor:
    namespaces = {}
    schemas = []

    def __init__(self, namespaces=None, schemas=None):
        self.namespaces = namespaces.copy() or {}
        self.schemas = schemas or []

    def accepts_request(self, request):
        """Return True if the instance is able to process the request.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        bool
            Whether this schema_processor is able to process the request.
        """

        raise NotImplementedError


class SchemaProcessor:
    namespace = ""

    def __init__(self, namespace):
        self.namespace = namespace

    def accepts_request(self, request):
        """Return True if the instance is able to process the request.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        bool
            Whether this schema_processor is able to process the request.
        """

        raise NotImplementedError
