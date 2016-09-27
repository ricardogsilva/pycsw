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

    def __init__(self, repository=None, federated_catalogues=None, **kwargs):
        super().__init__(**kwargs)
        self.distributed_search = (federated_catalogues if
                                   federated_catalogues is not None
                                   else CswDistributedSearch())
        self.repository = repository

    def get_urls(self):
        urls = []
        for host_url in self.server.public_hosts:
            for op in self.operations:
                url = "".join((host_url, self.server.site_name, self.url_path))
                for verb in (HttpVerb.GET, HttpVerb.POST):
                    if verb in op.allowed_http_verbs:
                        urls.append((op, verb, url))
        return urls


class CswOgcSchemaProcessor(servicebase.RequestParser):
    type_names = None
    record_mapping = None
    element_set_names = None

    def __init__(self, type_names=None, record_mapping=None,
                 element_set_names=None):
        super().__init__()
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
            raise exceptions.PycswError("{0} unable to parse "
                                        "general request info".format(self))
        else:
            return info

    def parse_request(self, request):
        try:
            request_info = self.parse_general_request_info(request)
            operation = [op for op in self.service.operations if
                         op.name == request_info["request"]][0]
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
        except (IndexError):
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
    media_type = "text/xml"

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
