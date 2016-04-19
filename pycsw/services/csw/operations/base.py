import logging
import inspect

from ....httprequest import HttpVerb
from ....exceptions import CswError
from ....exceptions import VERSION_NEGOTIATION_FAILED
from ....exceptions import INVALID_PARAMETER_VALUE
from ....exceptions import INVALID_UPDATE_SEQUENCE
from ....exceptions import NO_APPLICABLE_CODE

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

    def extract_kvp_parameters(self, request):
        """Reimplement in child classes."""
        raise NotImplementedError

    def extract_xml_parameters(self, request):
        """Reimplement in child classes."""
        raise NotImplementedError


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


    def __init__(self, enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        # OGC CSWv2.0.2 mandates that GetCapabilities
        # must accept GET requests
        self.allowed_http_verbs.add(HttpVerb.GET)
        self.parameters = [
            OperationParameter(name="AcceptVersions"),
            OperationParameter(name="Sections",
                               allowed_values=self._sections_map.keys()),
            OperationParameter(name="AcceptFormats"),
            OperationParameter(name="updateSequence", allowed_values=[1]),
        ]
        self.constraints = []

    def __call__(self, accept_versions=None, sections=None,
                 update_sequence=None, accept_formats=None):
        logger.debug("{0.__class__.__name__} called".format(self))
        service_to_use = self.get_service_to_use(accept_versions or [])
        if service_to_use is self.service:
            up_sequence = self.get_parameter(
                "updateSequence").allowed_values[0]
            result = {
                "version": self.service.version,
                "updateSequence": up_sequence,
            }
            if update_sequence is None or update_sequence < up_sequence:
                # return full capabilities
                sections_info = self.get_sections(sections)
                result.update(sections_info)
            elif update_sequence == up_sequence:
                pass  # result is complete, no need to add anything else
            else:
                raise CswError(code=INVALID_UPDATE_SEQUENCE)
        elif service_to_use is not None:
            # check if the GetCapabilities operation of the service_to_use
            # is enabled if so, process it and return the result
            other_get_capabilities = service_to_use.get_enabled_operation(
                "GetCapabilities")
            if other_get_capabilities is not None:
                logger.debug("Transferring operation {0.name} to "
                             "service {1}...".format(self, service_to_use))
                result = other_get_capabilities(
                    accept_versions=accept_versions,
                    sections=sections,
                    update_sequence=update_sequence,
                    accept_formats=accept_formats
                )
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

    def extract_kvp_parameters(self, request):
        if HttpVerb.GET in self.allowed_http_verbs:
            result = {
                "sections": request.parameters.get("sections"),
                "accept_versions": request.parameters.get("acceptVersions"),
                "accept_formats": request.parameters.get("acceptFormats"),
                "update_sequence": request.parameters.get("updateSequence"),
            }
        else:  # the operation does not respond to the input HTTP method
            raise CswError(code=NO_APPLICABLE_CODE)
        return result

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

    def get_parameter(self, name):
        for parameter in self.parameters:
            if parameter.name == name:
                result = parameter
                break
        else:
            result = None
        return result

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


class GetRecordById202Operation(CswOperation):
    _name = "GetRecordById"

    def __init__(self, enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        self.parameters = [
            OperationParameter(name="Id"),
            OperationParameter(name="ElementSetName"),
            OperationParameter(name="outputFormat"),
            OperationParameter(name="outputSchema"),
        ]
        self.constraints = []

    def __call__(self, id=None, element_set_name=None,
                 output_format=None, output_schema=None):
        logger.debug("{0.__class__.__name__} called".format(self))

    def extract_kvp_parameters(self, request):
        if HttpVerb.GET in self.allowed_http_verbs:
            result = {
                "id": ",".split(request.parameters.get("Id")),
                "element_set_name": request.parameters.get("ElementSetName"),
                "output_format": request.parameters.get("outputFormat"),
                "output_schema": request.parameters.get("outputSchema"),
            }
        else:  # the operation does not respond to the input HTTP method
            raise CswError(code=NO_APPLICABLE_CODE)
        return result
