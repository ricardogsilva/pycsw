import logging

from lxml import etree

from ... import exceptions
from .. import servicebase
from ...httprequest import HttpVerb

logger = logging.getLogger(__name__)


class CswDistributedSearch:
    """Manages distributed search."""

    def __init__(self, enabled=False, remote_catalogues=None, hop_count=1):
        self.enabled = enabled
        self.remote_catalogues = remote_catalogues or []
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
    distributed_search = CswDistributedSearch()
    operations = []

    def __init__(self, enabled, distributed_search=None, operations=None):
        super().__init__(enabled)
        # load config
        # load eventual plugins
        # lazy load operations
        self.distributed_search = distributed_search or CswDistributedSearch()
        self.operations = operations or []

    @classmethod
    def from_config(cls, **config):
        distributed_search = CswDistributedSearch.from_config(
            **config.get("distributed_search", {}))
        content_types = [CswContentTypeProcessor.from_config(**c) for c
                         in config.get("content_types", [])]
        kvp_types = [CswKvpProcessor.from_config(**c) for c
                     in config.get("kvp_types", [])]
        return cls(
            enabled=config.get("enabled", False),
            distributed_search=distributed_search,
            content_types=content_types,
        )

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

        result = None
        for processor in (p for p in self.kvp_processors +
                self.content_type_processors):
            logger.debug("Evaluating processor: {}...".format(processor))
            schema_to_use = processor.get_schema_processor(request)
            if schema_to_use is not None:
                logger.debug("Processor accepts request")
                result = schema_to_use
            else:
                logger.debug("Processor cannot accept request")
        else:
            logger.debug("Service {0.identifier} does not accept "
                         "the request".format(self))
        return result


class CswKvpProcessor(servicebase.RequestProcessor):
    name = ""

    def __init__(self, name, namespaces=None):
        self.name = name
        super().__init__(namespaces=namespaces)

    def __str__(self):
        return self.name

    def get_schema_processor(self, request):
        schema_to_use = None
        for schema in self.schemas:
            try:
                requested_info = schema.parse_general_request_info(request)
                service_ok = requested_info["service"] == self.service.name
                version_ok = requested_info["version"] == self.service.version
                if service_ok and version_ok:
                    schema_to_use = schema
                    break
            except exceptions.CswError:
                logger.debug("Schema {0.namespace} cannot accept "
                             "request".format(schema))
        else:
            logger.debug("Processor {} cannot accept request.".format(self))
        return schema_to_use


class CswContentTypeProcessor(servicebase.RequestProcessor):
    media_type = ""

    def __init__(self, media_type, namespaces=None):
        self.media_type = media_type
        super().__init__(namespaces=namespaces)

    def __str__(self):
        return self.media_type


class CswSchemaProcessor(servicebase.SchemaProcessor):
    type_names = []
    record_mapping = {}
    element_set_names = []

    def __init__(self, namespace, type_names=None, record_mapping=None,
                 element_set_names=None):
        super().__init__(namespace)
        self.type_names = type_names or []
        self.record_mapping = record_mapping or {}
        self.element_set_names = element_set_names or []

    @classmethod
    def from_config(cls, **config):
        return cls(
            namespace=config["namespace"],
            type_names=config.get("type_names"),
            record_mapping=config.get("record_mapping"),
            element_set_names=config.get("element_set_names"),
        )


class CswContentTypeSchemaProcessor(CswSchemaProcessor):

    def parse_general_request_info(self, request):
        return {
            "request": etree.QName(request.exml).localname,
            "service": request.exml.get("service"),
            "version": request.exml.get("version"),
        }


class CswKvpSchemaProcessor(CswSchemaProcessor):

    def parse_general_request_info(self, request):
        return {
            "request": request.parameters.get("request"),
            "service": request.parameters.get("service"),
            "version": request.parameters.get("version"),
        }
