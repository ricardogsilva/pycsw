"""Pycsw server class.

>>> server = PycswServer()
>>> # request is a PycswHttpRequest that was created from the werkzeug request
>>> try:
>>>     parser = server.get_request_parser(request)
>>>     operation, parameters = parser.parse_request(request)
>>>     operation.prepare(**parameters)
>>>     service = parser.service
>>>     response_renderer = service.get_renderer(operation, request)
>>>     response, status_code = operation()
>>>     rendered, headers = response_renderer.render(element=operation.name,
>>>                                                  **response)
>>> except PycswError as err:
>>>     response = server.generate_error_response(err)
>>> finally:  # wrap our response as a werkzeug response
>>>     return rendered_response, status_code, headers

"""

import logging
import os

import yaml

from . import contacts
from . import exceptions
from . import utilities
#from .httprequest import HttpVerb
#from .repositories.sla.repository import CswSlaRepository
#from .services.csw import csw202
#from .services.csw import cswbase
#from .services.csw.responserenderers import renderers
#from .services.csw.operations.getcapabilities import (
#    GetCapabilities202OperationProcessor)
#from .services.csw.operations.getrecordbyid import (
#    GetRecordById202Operation)

logger = logging.getLogger(__name__)


class PycswServer:
    """Processes incoming HTTP requests."""

    provider_name = ""
    provider_site = None
    provider_contact = None
    site_name = ""  # used for building URLs for the server
    public_host = ""  # used for building URLs for the server

    _services = None

    def __init__(self, config_path=None, **config_args):
        logger.info("Initializing server...")
        config = self.load_config(config_path=config_path, **config_args)
        self.public_host = config.get(
            "server", {}).get("endpoint", "http://localhost:8000/")
        self.provider_name = config.get("provider", {}).get(
            "name", "Placeholder name")
        self.provider_site = contacts.IsoOnlineResource(
            linkage=config.get("provider", {}).get("url", ""))
        self.provider_contact = contacts.IsoResponsibleParty.from_config(config)
        self._services = utilities.ManagedList(manager=self,
                                               related_name="_server")
        self.load_services(config)
        #csw202_repository = self.setup_csw202_repository()
        #csw202_service = self.setup_csw202_service(
        #    repository=csw202_repository)
        #self.services.append(csw202_service)
        #self.finish_loading_csw_services()

    def __repr__(self):
        return ("{0.__class__.__name__}(services={0.services!r})".format(self))

    @property
    def services(self):
        return self._services

    # DEPRECATED
    #@classmethod
    #def setup_csw202_service(cls, repository=None):
    #    """Create the CSW version 2.0.2 service."""
    #    ogc_record_mapping = {
    #        "title": "dc:title",
    #        "creator": "dc:creator",
    #        "subject": "dc:subject",
    #        "abstract": "dct:abstract",
    #        "publisher": "dc:publisher",
    #        "contributor": "dc:contributor",
    #        "modified": "dct:modified",
    #        "type_": "dc:type",
    #        "format_": "dc:format",
    #        "identifier": "dc:identifier",
    #        "source": "dc:source",
    #        "language": "dc:language",
    #        "association": "dc:relation",
    #        "bounding_box": "ows:BoundingBox",
    #        "rights": "dc:rights",
    #    }
    #    ogc_element_set_names = {
    #        "full": [
    #            "dc:identifier",
    #            "dc:title",
    #            "dc:creator",
    #            "dc:subject",
    #            "dct:abstract",
    #            "dc:publisher",
    #            "dc:contributor",
    #            "dct:modified",
    #            "dc:type",
    #            "dc:format",
    #            "dc:source",
    #            "dc:language",
    #            "dc:relation",
    #            "ows:BoundingBox",
    #            "dc:rights",
    #        ],
    #        "summary": [
    #            "dc:identifier",
    #            "dc:title",
    #            "dc:type",
    #            "dc:subject",
    #            "dc:format",
    #            "dc:relation",
    #            "dct:modified",
    #            "dct:abstract",
    #            "dct:spatial",  # ?
    #            "ows:BoundingBox",
    #        ],
    #        "brief": [
    #            "dc:identifier",
    #            "dc:title",
    #            "dc:type",
    #            "ows:BoundingBox",
    #        ],
    #    }
    #    # schema_processors
    #    post_processor = cswbase.CswOgcPostProcessor(
    #        type_names=["csw:Record"],
    #        record_mapping=ogc_record_mapping,
    #        element_set_names=ogc_element_set_names,
    #    )

    #    kvp_processor = cswbase.CswOgcKvpProcessor(
    #        type_names=["csw:Record"],
    #        record_mapping=ogc_record_mapping,
    #        element_set_names=ogc_element_set_names,
    #    )
    #    # operations
    #    get_capabilities = GetCapabilities202OperationProcessor(
    #        enabled=True,
    #        allowed_http_verbs={HttpVerb.GET}
    #    )
    #    get_record_by_id = GetRecordById202Operation(
    #        enabled=True,
    #        allowed_http_verbs={HttpVerb.GET}
    #    )
    #    csw202_service = csw202.Csw202Service(
    #        distributed_search=cswbase.CswDistributedSearch(),
    #        repository=repository,
    #    )
    #    csw202_service.request_parsers.append(post_processor)
    #    csw202_service.request_parsers.append(kvp_processor)
    #    csw202_service.operations.append(get_capabilities)
    #    csw202_service.operations.append(get_record_by_id)

    #    csw202_service.response_renderers.append(
    #        renderers.OgcCswXmlRenderer())

    #    logger.debug("Initialized csw202 service")
    #    return csw202_service

    # DEPRECATED
    #def setup_csw202_repository(self, engine_url=None, echo=False,
    #                            query_translator_modules=None):
    #    repository = CswSlaRepository(
    #        engine_url=engine_url,
    #        echo=echo,
    #        query_translator_modules=query_translator_modules
    #    )
    #    return repository

    def get_service(self, name, version):
        """Return the service with the specified name and version."""
        for service in self.services:
            if (service.name.lower() == name.lower() and
                    service.version == version):
                return service
        else:
            logger.debug("Server does not feature "
                         "service {}v{}".format(name, version))

    def get_request_parser(self, request):
        """Get the appropriate RequestParser to process the incoming request.

        This method selects the RequestParser that is suitable for
        processing the request among the list of currently enabled services.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        service: pycsw.services.servicebase.SchemaProcessor or None
            The schema_processor object that can process the request.

        Raises
        ------
        pycsw.exceptions.PycswError
            If none of the enabled services has a schema_processor that can
            process the request.

        """
        for service in self.services:
            logger.debug("Evaluating service {0.identifier}...".format(
                service))
            parser = service.get_request_parser(request)
            if parser is not None:
                # stop on the first suitable service
                logger.info("{} can handle the request".format(
                    parser))
                return parser
        else:
            raise exceptions.PycswError("Could not find a suitable "
                                        "RequestParser in any of the "
                                        "available services.")

    # FIXME: DEPRECATED
    #def finish_loading_csw_services(self):
    #    """Update metadata on CSW services after the have been loaded.

    #    This method is specially relevant for the GetCapabilities operations
    #    defined in each available CSW service. Since GetCapabilities accepts
    #    the `AcceptVersions` parameter, it becomes necessary to let each
    #    GetCapabilities operation instance know about the various CSW services
    #    that are available on the server.

    #    """
    #    csw_versions = [s.version for s in self.services if s.name == "CSW"]

    #    for service in (s for s in self.services if s.name == "CSW"):
    #        try:
    #           op = service.get_enabled_operation("GetCapabilities")
    #        except exceptions.PycswError:
    #            continue  # this service doesn't have a GetCapabilities
    #        else:
    #            allowed_values = {
    #                "accept_versions": csw_versions,
    #                "accept_formats": [p.media_type for p in
    #                                   service.request_parsers if
    #                                   p.media_type],
    #            }
    #            defaults = {
    #                "accept_versions": [self.default_csw_service.version],
    #                "accept_formats": [
    #                    self.default_csw_service.default_output_format],
    #            }
    #            op.update_parameter_allowed_values(**allowed_values)
    #            op.update_parameter_defaults(**defaults)

    def load_services(self, config):
        """Load the services specified in the input config."""
        # TODO: must load some sensible defaults in case config is empty
        for service_name, service_params in config.get("services", {}).items():
            for version_name in [param for param in service_params if
                                 param.startswith("version_")]:
                version_params = service_params[version_name]
                if version_params.get("enabled", False):
                    logger.debug("Loading service {0} {1}...".format(
                        service_name, version_name))
                    module_path, class_ = version_params["class"].rpartition(
                        ".")[::2]
                    LoadedClass = utilities.lazy_import_dependency(
                        module_path, class_)
                    service = LoadedClass.from_config(config)
                    self._services.append(service)

    def get_default_service(self, service_name):
        """Return the service that responds to requests with no version.

        Since the GetCapabilities request does not mandate the presence of the
        'version' parameter, there must be a default service for each
        servie class. The default service is found in one of two ways:

        * The first service instance that has the 'default' attribute set to
          a truthy value, it becomes the default;
        * If none of the currently configured services has the 'default'
          attribute set to a truthy value, a sorting is performed and the
          latest version is considered the new default. By latest we mean the
          one that is sorted first in descending order when sorted
          alphabetically.

        """

        default_service = None
        for service in (s for s in self.services if
                        s.name.lower() == service_name.lower()):
            if service.is_default_version:
                default_service = service
                break
            else:
                try:
                    default_service = sorted(
                        (service.version, default_service), reverse=True)[0]
                except TypeError:  # latest_service is None
                    default_service = service
        return default_service

    @classmethod
    def load_config(cls, config_path=None, **config_keys):
        """Load server configuration.

        Configuration may be loaded using several methods:

        * By passing the path to a configuration file to be read. The
          configuration file must be valid yaml. It is also possible to
          specify the config file's path with the
          ``PYCSW_CONFIG_PATH`` environment variable instead;

        * By using environment variables. In this case, every variable must
          be defined as PYCSW_SECTION__VARIABLE=value (note the usage of
          double underscore to separate sections from variable names). This
          method of specifying configuration values takes precedence over
          configuration files;

        * By passing individual name=value pairs. The variable name is
          defined in the same way as when passing environment variables:
          PYCSW_SECTION__SUB_SECTION__VARIABLE;

        Section and variable names are case insensitive. Variable values are
        case sensitive though.

        Parameters
        ----------
        config_path: str, optional
            Full path to the YAML file where settings are specified.

        Returns
        -------
        dict
            The parsed configuration settings

        """

        config = cls._load_config_from_path(config_path)
        cls._update_config_from_environment(config)
        cls._update_config_from_kwargs(config, **config_keys)
        return config

    @classmethod
    def _load_config_from_path(cls, config_path=None):
        config = {}
        path = config_path or os.environ.get("PYCSW_CONFIG_PATH")
        if path is not None:
            logger.debug("Loading configuration from {0!r}...".format(path))
            with open(path) as fh:
                config.update(yaml.safe_load(fh))
        return config

    @classmethod
    def _update_config_from_environment(cls, config):
        env_kwargs = {k: v for k, v in os.environ.items() if
                      k.lower().startswith("pycsw_") and
                      k.lower() != "pycsw_config_path"}
        if len(env_kwargs) > 0:
            logger.debug("Updating configuration from environment variables...")
        cls._update_config_from_kwargs(config, **env_kwargs)

    @classmethod
    def _update_config_from_kwargs(cls, config, **kwargs):
        operate_on = config
        for key, value in ((k, v) for k, v in kwargs.items() if
                           k.lower().startswith("pycsw_")):
            sections = key.lower().replace("pycsw_", "").split("__")
            variable = sections.pop()
            for section in sections:
                if operate_on.get(section) is None:
                    operate_on[section] = {}
                operate_on = operate_on[section]
            operate_on[variable] = value
            operate_on = config

