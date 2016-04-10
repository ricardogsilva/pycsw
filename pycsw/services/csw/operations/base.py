import logging
import inspect

from ....httprequest import HttpVerb
from ....exceptions import CswError
from ....exceptions import VERSION_NEGOTIATION_FAILED
from ....exceptions import INVALID_PARAMETER_VALUE

logger = logging.getLogger(__name__)


class CswOperation:
    """Base class for all CSW operations.

    All CSW operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    """

    _name = ""
    _service = None
    parameters = None
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


class OperationParameter:

    name = ""
    allowed_values = ""
    metadata = None

    def __init__(self, name, allowed_values=None, metadata=None):
        self.name = name
        self.allowed_values = (list(allowed_values) if
                               allowed_values is not None else allowed_values)
        self.metadata = metadata

    def __str__(self):
        return "{0.__class__.__name__}(name={0.name})".format(self)

    def __repr__(self):
        return ("{0.__class__.__name__}(name={0.name!r}, "
                "allowed_values={0.allowed_values!r}, "
                "metadata={0.metadata!r})".format(self))


class GetCapabilities202Operation(CswOperation):
    _name = "GetCapabilities"

    parameters = [
        OperationParameter(name="AcceptVersions"),
        OperationParameter(name="Sections"),
        OperationParameter(name="AcceptFormats"),
        OperationParameter(name="updateSequence"),
    ]
    constraints = []

    def __init__(self, enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        # OGC CSWv2.0.2 mandates that GetCapabilities
        # must accept GET requests
        self.allowed_http_verbs.add(HttpVerb.GET)

    def __call__(self, accept_versions=None, sections=None,
                 update_sequence=None, accept_formats=None):
        logger.debug("{0.__class__.__name__} called".format(self))
        service_to_use = self.get_service_to_use(accept_versions or [])
        if service_to_use is self.service:
            sections_info = self.get_sections(sections)
        elif service_to_use is not None:
            # check if the GetCapabilities operation of the service_to_use
            # is enabled if so, process it and return the result
            pass
        else:
            raise CswError(code=VERSION_NEGOTIATION_FAILED)

    def get_service_to_use(self, accept_versions):
        service = None
        if any(accept_versions):
            for requested in accept_versions:
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
        section_map = {
            "ServiceIdentification": self.get_service_identification,
            "ServiceProvider": self.get_service_provider,
            "OperationsMetadata": self.get_service_provider,
            "Contents": self.get_contents,
            "FilterCapabilities": self.get_filter_capabilities,
        }
        for name in (s for s in sections):
            if name not in section_map.keys() and name != "All":
                raise CswError(code=INVALID_PARAMETER_VALUE,
                                locator="Sections")
        else:
            for name, func in section_map.items():
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
