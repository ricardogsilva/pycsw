"""Pycsw server class.

>>> server = PycswServer(config)
>>> # request is a PycswHttpRequest that was created from the werkzeug request
>>> try:
>>>     processor = server.get_schema_processor(request)
>>>     response = processor.process_request(request)
>>> except PycswError as err:
>>>     response = server.generate_error_response(err)
>>> finally:  # wrap our response as a werkzeug response
>>>     return response

"""

import logging

from . import exceptions
from .services.csw import cswbase
from .services.csw import csw202
from .services.csw.operations import base
from .httprequest import HttpVerb
from .repositories.sla.repository import CswSlaRepository
from . import utilities
from . import contacts

logger = logging.getLogger(__name__)


class PycswServer:
    """Processes incoming HTTTP requests."""

    provider_name = ""
    provider_site = None
    provider_contact = None

    _services = None

    def __init__(self, config_path=None, **config_args):
        # load common config for all services.
        config = {}
        self.provider_name = config.get("name", config_args.get("name", ""))
        # todo: add site and contact details
        self.provider_site = contacts.IsoOnlineResource(linkage="")
        self.provider_contact = contacts.IsoResponsibleParty()
        logger.debug("Initializing server...")
        self._services = utilities.ManagedList(manager=self,
                                               related_name="_server")
        csw202_repository = self.setup_csw202_repository()
        csw202_service = self.setup_csw202_service(
            repository=csw202_repository)
        self.services.append(csw202_service)
        self.finish_loading_csw_services()

    def __repr__(self):
        return ("{0.__class__.__name__}(services={0.services!r}, "
                "default_csw_service={0.default_csw_service!r})".format(self))

    @property
    def services(self):
        return self._services

    @property
    def default_csw_service(self):
        """Return the service that responds to CSW requests with no version.

        Since the GetCapabilities request does not mandate the presence of the
        'version' parameter, there must be a default CSW service. The service
        that handles CSW with the latest version among the currently enabled
        services is returned.
        """
        latest_csw = None
        for service in (s for s in self.services if s.name == "CSW"):
            try:
                 latest_csw = sorted((service.version, latest_csw),
                                     reverse=True)[0]
            except TypeError:  # latest_csw is None
                latest_csw = service
        return latest_csw

    @classmethod
    def setup_csw202_service(cls, repository=None):
        """Create the CSW version 2.0.2 service."""
        ogc_namespaces = {
            "csw": "http://www.opengis.net/cat/csw/2.0.2",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "ows": "http://www.opengis.net/ows",

        }
        ogc_record_mapping = {
            "title": "dc:title",
            "creator": "dc:creator",
            "subject": "dc:subject",
            "abstract": "dct:abstract",
            "publisher": "dc:publisher",
            "contributor": "dc:contributor",
            "modified": "dct:modified",
            "type_": "dc:type",
            "format_": "dc:format",
            "identifier": "dc:identifier",
            "source": "dc:source",
            "language": "dc:language",
            "association": "dc:relation",
            "bounding_box": "ows:BoundingBox",
            "rights": "dc:rights",
        }
        ogc_element_set_names = {
            "full": [
                "dc:identifier",
                "dc:title",
                "dc:creator",
                "dc:subject",
                "dct:abstract",
                "dc:publisher",
                "dc:contributor",
                "dct:modified",
                "dc:type",
                "dc:format",
                "dc:source",
                "dc:language",
                "dc:relation",
                "ows:BoundingBox",
                "dc:rights",
            ],
            "summary": [
                "dc:identifier",
                "dc:title",
                "dc:type",
                "dc:subject",
                "dc:format",
                "dc:relation",
                "dct:modified",
                "dct:abstract",
                "dct:spatial",  # ?
                "ows:BoundingBox",
            ],
            "brief": [
                "dc:identifier",
                "dc:title",
                "dc:type",
                "ows:BoundingBox",
            ],
        }
        post_processor = cswbase.CswOgcPostProcessor(
            media_type="application/xml",
            namespaces=ogc_namespaces,
            type_names=["csw:Record"],
            record_mapping=ogc_record_mapping,
            element_set_names=ogc_element_set_names,
        )

        kvp_processor = cswbase.CswOgcKvpProcessor(
            namespaces=ogc_namespaces,
            type_names=["csw:Record"],
            record_mapping=ogc_record_mapping,
            element_set_names=ogc_element_set_names,
        )
        get_capabilities = base.GetCapabilities202Operation(
            enabled=True,
            allowed_http_verbs={HttpVerb.GET}
        )
        get_record_by_id = base.GetRecordById202Operation(
            enabled=True,
            allowed_http_verbs={HttpVerb.GET}
        )
        csw202_service = csw202.Csw202Service(
            distributed_search=cswbase.CswDistributedSearch(),
            repository=repository,
        )
        csw202_service.schema_processors.append(post_processor)
        csw202_service.schema_processors.append(kvp_processor)
        csw202_service.operations.append(get_capabilities)
        csw202_service.operations.append(get_record_by_id)
        logger.debug("Initialized csw202 service")
        return csw202_service

    def setup_csw202_repository(self, engine_url=None, echo=False,
                                query_translator_modules=None):
        repository = CswSlaRepository(
            engine_url=engine_url,
            echo=echo,
            query_translator_modules=query_translator_modules
        )
        return repository

    def get_service(self, name, version):
        """Return the service with the specified name and version."""
        for s in self.services:
            if s.name == name and s.version == version:
                return s
        else:
            logger.debug("Server does not feature "
                         "service {}v{}".format(name, version))

    def get_schema_processor(self, request):
        """Get the appropriate schema_processor to process the incoming request.

        This method selects the schema_processor that is suitable for
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
            logger.debug("Evaluating {0.identifier}...".format(service))
            schema_processor = service.get_schema_processor(request)
            if schema_processor is not None:
                # stop on the first suitable service
                return schema_processor
        else:
            raise exceptions.PycswError("Could not find a suitable schema "
                                        "processor in any of the available "
                                        "services.")

    def finish_loading_csw_services(self):
        """Update metadata on CSW services after the have been loaded.

        This method is specially relevant for the GetCapabilities operations
        defined in each available CSW service. Since GetCapabilities accepts
        the `AcceptVersions` parameter, it becomes necessary to let each
        GetCapabilities operation instance know about the various CSW services
        that are available on the server.

        """
        csw_versions = [s.version for s in self.services if s.name == "CSW"]

        for csw_service in (s for s in self.services if s.name == "CSW"):
            get_capabilities = csw_service.get_enabled_operation(
                "GetCapabilities")
            if get_capabilities is not None:
                accept_versions = get_capabilities.get_parameter(
                    "AcceptVersions")
                accept_versions.allowed_values = csw_versions
                accept_formats = get_capabilities.get_parameter(
                    "AcceptFormats")
                accept_formats.allowed_values = [
                    p.media_type for p in csw_service.schema_processors if
                    p.media_type
                ]

