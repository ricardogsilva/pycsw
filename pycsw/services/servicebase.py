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
    """Base class for all pycsw services.

    Parameters
    ----------

    title: str, optional
        The title of the service.
    abstract: str, optional
        The abstract of the service.
    keywords: list, optional
        An iterable with strings that are the metadata keywords for the
        service
    keywords_type: str, optional
        The Type of the keywords according to ISO19115 MD_KeywordTypeCode
        codelist.
    fees: str, optional
        The fees, if any, for using the service
    access_constraints: str, optional
        Access constraints for the service
    enabled: bool, optional
        Is the service enabled
    operations: dict
        The set of operations that the service implements. This mapping can
    """

    title = ""
    url_path = ""  # used for building URLs for the service
    abstract = ""
    keywords = None
    keywords_type = ""
    fees = ""
    access_constraints = ""
    namespaces = {}
    enabled = False
    is_default_version = False

    _name = ""  # Must be set by each subclass
    _version = ""  # Must be set by each subclass

    _server = None  # Is set by the server

    request_parsers = None
    response_renderers = None

    def __init__(self, title="", abstract="", keywords=None, keywords_type="",
                 fees="", access_constraints="", enabled=False, default=False,
                 operations=None, request_parsers=None,
                 response_renderers=None):
        self.title = title or self._name
        self.abstract = abstract or self._name
        self.keywords = list(keywords) if keywords is not None else []
        self.keywords_type = keywords_type
        self.fees = fees
        self.access_constraints = access_constraints
        self.enabled = enabled
        self.is_default_version = default
        self.operations = self._load_operations(operations or {})
        self.request_parsers = utilities.LazyManagedList(
            contents=request_parsers or [],
            manager=self,
            related_name="_service"
        )
        self.response_renderers = utilities.LazyManagedList(
            contents=response_renderers or [],
            manager=self,
            related_name="_service"
        )

        self.namespaces =  {}
        self._server = None

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

    @classmethod
    def from_config(cls, config):
        """Create a new instance from the global pycsw config.

        Parameters
        ----------
        config: dict
            The pycsw configuration that is being used. This dict must use
            the same layout as the one returned by
            ``pycsw.server.PycswServer.load_config``

        """

        try:
            service_config = config["services"][cls._name.lower()].copy()
            version_config = service_config.pop("version_{0}".format(
                cls._version))
        except KeyError:
            service_config = {}
            version_config = {}
        else:
            # lets remove keys from service_config and version_config that
            # are not needed and are not recognized by
            # ServiceBase.from_config()
            versions_to_pop = [other for other in service_config if
                               other.startswith("version_")]
            for other_version in versions_to_pop:
                service_config.pop(other_version)
            version_config.pop("class")
        return cls(
            title=service_config.pop("title", cls.identifier),
            abstract=service_config.pop("abstract", ""),
            keywords=service_config.pop("keywords"),
            keywords_type=service_config.pop("keywords_type", ""),
            fees=service_config.pop("fees", ""),
            access_constraints=service_config.pop("access_constraints", ""),
            enabled=version_config.pop("enabled", False),
            operations=version_config.pop("operations", {}),
            request_parsers=version_config.pop("request_parsers"),
            response_renderers=version_config.pop("response_renderers"),
            **service_config,
            **version_config
        )

    def get_request_parser(self, request):
        """Get a suitable RequestParser object for the request

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        RequestParser
            The request_parser object that can process the request.

        """

        for parser in self.request_parsers:
            logger.debug("Evaluating request with {0}...".format(parser))
            try:
                info = parser.parse_general_request_info(request)
            except exceptions.PycswError:
                logger.debug("{0} cannot accept request".format(parser))
            else:
                logger.debug("requested_info: {}".format(info))
                service_ok = info["service"] == self.name
                version_ok = info["version"] == self.version
                is_default = self.server.get_default_service(
                    self.name) is self
                logger.debug("service_ok: {}".format(service_ok))
                logger.debug("version_ok: {}".format(version_ok))
                logger.debug("is_default: {}".format(is_default))
                if service_ok:
                    if version_ok or (info["version"] is None and is_default):
                        return parser
        else:
            logger.debug("Service {0.identifier} cannot accept "
                         "request.".format(self))

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

    def _load_operations(self, operations_config):
        """Load the input operations.

        Parameters
        ----------
        operations_config: dict
            A mapping with the configured operations.

        """

        container = utilities.LazyManagedList(manager=self,
                                              related_name="_service")
        for op_name, op_params in operations_config.items():
            class_ = op_params.pop("class")
            if op_params.pop("enabled", False):
                container.append((class_, op_params))
        return container


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
