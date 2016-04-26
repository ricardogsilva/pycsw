import logging

from . import parameters
from pycsw.httprequest import HttpVerb
from pycsw.exceptions import CswError
from pycsw.exceptions import VERSION_NEGOTIATION_FAILED
from pycsw.exceptions import INVALID_PARAMETER_VALUE
from pycsw.exceptions import INVALID_UPDATE_SEQUENCE

logger = logging.getLogger(__name__)


class CswOperationProcessor:
    """Base class for all CSW operations.

    All CSW operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    """

    _name = ""
    _service = None
    constraints = None
    enabled = False
    allowed_http_verbs = None


    def __init__(self, enabled=True, allowed_http_verbs=None):
        self._service = None
        self.enabled = enabled
        self.allowed_http_verbs = (set(allowed_http_verbs) if
                                   allowed_http_verbs is not None else set())

    def __str__(self):
        return "{0.__class__.__name__}({0.service}, {0.name})".format(self)


    @property
    def name(self):
        return self._name

    @property
    def service(self):
        return self._service


class GetCapabilities202OperationProcessor(CswOperationProcessor):
    _name = "GetCapabilities"

    accept_versions = parameters.TextListParameter("AcceptVersions",
                                                   optional=True)
    sections = parameters.TextListParameter("Sections", optional=True)
    accept_formats = parameters.TextListParameter("AcceptFormats",
                                                  optional=True)
    update_sequence = parameters.IntParameter("updateSequence",
                                              optional=True,
                                              allowed_values=[1],
                                              default=1)


    def __init__(self, accept_versions=None, sections=None,
                 accept_formats=None, update_sequence=None,
                 enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        # OGC CSWv2.0.2 mandates that GetCapabilities
        # must accept GET requests
        self.allowed_http_verbs.add(HttpVerb.GET)
        self.__class__.sections.allowed_values = self._sections_map.keys()
        self.accept_versions = accept_versions
        self.sections = sections
        self.accept_formats = accept_formats
        self.update_sequence = update_sequence
        self.constraints = []

    def __call__(self):
        service_to_use = self.get_service_to_use()
        if service_to_use is self.service:
            result = {
                "version": self.service.version,
                "updateSequence": self.update_sequence,
            }
            latest = self.__class__.update_sequence.allowed_values[-1]
            if self.update_sequence < latest:
                # return full capabilities
                sections_info = self.get_sections(self.sections)
                result.update(sections_info)
            elif self.update_sequence == latest:
                pass  # result is complete, no need to add anything else
            else:
                raise CswError(code=INVALID_UPDATE_SEQUENCE)
        elif service_to_use is not None:
            # check if the GetCapabilities operation of the service_to_use
            # is enabled if so, process it and return the result
            other_get_capabilities = service_to_use.get_enabled_operation(
                "GetCapabilities", accept_versions=self.accept_versions,
                sections=self.sections, accept_formats=self.accept_formats,
                update_sequence=self.update_sequence
            )
            result = other_get_capabilities()
            if other_get_capabilities is not None:
                logger.debug("Transferring operation {0.name} to "
                             "service {1}...".format(self, service_to_use))
            else:
                raise CswError(code=VERSION_NEGOTIATION_FAILED)
        else:
            raise CswError(code=VERSION_NEGOTIATION_FAILED)
        return result

    @property
    def _sections_map(self):
        return {
            "ServiceIdentification": self.get_service_identification,
            "ServiceProvider": self.get_service_provider,
            "OperationsMetadata": self.get_operations_metadata,
            "Contents": self.get_contents,
            "FilterCapabilities": self.get_filter_capabilities,
        }

    def get_service_to_use(self):
        service = None
        for requested in self.accept_versions:
            service = self.service.server.get_service(
                self.service.name, requested)
            if service is not None:
                break
        else:
            service = self.service.server.default_csw_service
        return service

    def get_sections(self, sections=None):
        sections = list(sections) if sections is not None else []
        result = {}
        for name in (s for s in sections):
            if name not in self._sections_map.keys() and name != "All":
                raise CswError(code=INVALID_PARAMETER_VALUE,
                                locator="Sections")
        else:
            for name, func in self._sections_map.items():
                if name in sections or not any(sections):
                    result[name] = func()
        return result

    def get_service_identification(self):
        return {
            "ServiceType": self.service.name,
            "ServiceTypeVersion": self.service.version,
            "Title": self.service.title,
            "Abstract": self.service.abstract,
            "Keywords": self.service.keywords,
            "Fees": self.service.fees,
            "AccessConstraints": self.service.access_constraints,
        }

    def get_service_provider(self):
        provider_contact = self.service.server.provider_contact
        provider_site = self.service.server.provider_site
        return {
            "ProviderName": self.service.server.provider_name,
            "ProviderSite": {
                "linkage": provider_site.linkage,
                "name": provider_site.name,
                "protocol": provider_site.protocol,
                "description": provider_site.description,
            },
            "ServiceContact": {
                "organisationName": provider_contact.organisation_name,
            }
        }

    def get_operations_metadata(self):
        ops = []
        for operation in self.service.operations:
            if operation.enabled:
                op_data = {
                    "name": operation.name,
                    "distributed_computing_platform": None,
                    "parameters": operation.parameters,
                    "constraints": operation.constraints,
                    "metadatas": [],
                }
                ops.append(op_data)
        return ops

    def get_filter_capabilities(self):
        pass

    def get_contents(self):
        pass


class GetRecordById202Operation(CswOperationProcessor):
    _name = "GetRecordById"

    id = parameters.TextParameter("Id")
    element_set_name = parameters.TextParameter(
        "ElementSetName", optional=True,
        allowed_values=["brief", "summary", "full"],
        default="brief"
    )
    output_format = parameters.TextParameter("outputFormat", optional=True,
                                             default="application/xml")
    output_schema = parameters.TextParameter(
        "outputSchema",
        optional=True,
        default="http://www.opengis.net/cat/csw/2.02"
    )

    def __init__(self, id, element_set_name=None, output_format=None,
                 output_schema=None, enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        self.constraints = []

    def __call__(self):
        logger.debug("{0.__class__.__name__} called".format(self))
