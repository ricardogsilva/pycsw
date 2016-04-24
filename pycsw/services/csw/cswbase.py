import logging

from lxml import etree

from .. import servicebase
from ... import exceptions
from ... httprequest import HttpVerb
from ...exceptions import OPERATION_NOT_SUPPORTED
from ...exceptions import NO_APPLICABLE_CODE

logger = logging.getLogger(__name__)


class CswDistributedSearch:
    """Manages distributed search."""

    def __init__(self, enabled=False, remote_catalogues=None, hop_count=1):
        self.enabled = enabled
        self.remote_catalogues = (list(remote_catalogues) if
                                  remote_catalogues is not None else [])
        self.hop_count = hop_count

    @classmethod
    def from_config(cls, **config):
        return cls(
            enabled=config.get("enabled", False),
            remote_catalogues=config.get("remote_catalogues"),
            hop_count=config.get("hop_count", 1),
        )


class CswService(servicebase.Service):
    """Base CSW implementation."""

    _name = "CSW"
    distributed_search = None
    repository = None

    def __init__(self, repository=None, distributed_search=None):
        super().__init__()
        self.distributed_search = (distributed_search if
                                   distributed_search is not None
                                   else CswDistributedSearch())
        self.repository = repository

    def get_schema_processor(self, request):
        """Get a suitable schema processor for the request

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.servicebase.SchemaProcessor or None
            The schema_processor object that is able to process the request.

        """

        schema_processor_to_use = None
        for processor in self.schema_processors:
            logger.debug("Evaluating {}...".format(processor))
            try:
                info = processor.parse_general_request_info(request)
                logger.debug("requested_info: {}".format(info))
                service_ok = info["service"] == self.name
                version_ok = info["version"] == self.version
                is_default = self.server.default_csw_service is self
                if service_ok and version_ok:
                    schema_processor_to_use = processor
                    break
                elif service_ok and info["version"] is None and is_default:
                    schema_processor_to_use = processor
                    break
            except exceptions.PycswError:
                logger.debug("SchemaProcessor {} cannot accept "
                             "request".format(processor))
        else:
            logger.debug("Service {0.identifier} cannot accept "
                         "request.".format(self))
        return schema_processor_to_use


class CswOgcSchemaProcessor(servicebase.SchemaProcessor):
    type_names = None
    record_mapping = None
    element_set_names = None

    def __init__(self, namespaces, media_type=None, type_names=None,
                 record_mapping=None, element_set_names=None):
        super().__init__(namespaces=namespaces, media_type=media_type)
        self.type_names = type_names if type_names is not None else []
        self.record_mapping = (record_mapping if record_mapping is not None
                               else {})
        self.element_set_names = (element_set_names if
                                  element_set_names is not None else {})


class CswOgcKvpProcessor(CswOgcSchemaProcessor):

    def parse_general_request_info(self, request):
        try:
            info = {
                "request": request.parameters.get("request"),
                "service": request.parameters.get("service"),
                "version": request.parameters.get("version"),
            }
        except KeyError:
            raise exceptions.PycswError("Processor {} unable to parse "
                                        "general request info".format(self))
        else:
            return info

    def parse_request(self, request):
        try:
            request_info = self.parse_general_request_info(request)
            operation = self.service.get_enabled_operation(
                request_info["request"])
            if HttpVerb.GET in operation.allowed_http_verbs:
                parameter_parser = {
                    "GetCapabilities": self.parse_get_capabilities,
                    "GetRecordById": self.parse_get_record_by_id,
                }.get(operation.name)
                parameters = parameter_parser(request)
            else: # the operation does not respond to the input HTTP method
                raise exceptions.CswError(code=NO_APPLICABLE_CODE)
        except exceptions.CswError:
            raise  # do we really need to do this?
        except (TypeError, exceptions.PycswError):
            raise exceptions.CswError(code=OPERATION_NOT_SUPPORTED)
        else:
            return operation, parameters

    def parse_get_capabilities(self, request):
        result = {
            "sections": request.parameters.get("sections"),
            "accept_versions": request.parameters.get("acceptVersions"),
            "accept_formats": request.parameters.get("acceptFormats"),
            "update_sequence": request.parameters.get("updateSequence"),
        }
        return result

    def parse_get_record_by_id(self, request):
        result = {
            "id": ",".split(request.parameters.get("Id")),
            "element_set_name": request.parameters.get("ElementSetName"),
            "output_format": request.parameters.get("outputFormat"),
            "output_schema": request.parameters.get("outputSchema"),
        }
        return result


class CswOgcPostProcessor(CswOgcSchemaProcessor):

    def parse_general_request_info(self, request):
        try:
            info = {
                "request": etree.QName(request.exml).localname,
                "service": request.exml.get("service"),
                "version": request.exml.get("version"),
            }
        except etree.XMLSyntaxError:
            raise exceptions.PycswError("Processor {} unable to parse "
                                        "general request info.".format(self))
