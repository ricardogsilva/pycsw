import logging

from ... import exceptions
from .. import base

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


class CswRequestProcessor:
    namespaces = {}
    schemas = []

    def __init__(self, namespaces=None, schemas=None):
        self.namespaces = namespaces.copy() or {}
        self.schemas = schemas or []

    def accepts_request(self, request):
        """Return True if the incoming request can be processed.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        bool
            Whether this processor can process the request or not.

        """

        raise NotImplementedError


class CswKvpProcessor(CswRequestProcessor):
    name = ""

    def __init__(self, name, namespaces=None, schemas=None):
        self.name = name
        super().__init__(namespaces=namespaces, schemas=schemas)

    def __str__(self):
        return self.name

    @classmethod
    def from_config(cls, **config):
        schemas = [CswSchemaProcessor.from_config(**schema_config) for
                   schema_config in config.get("schemas", [])]
        return cls(
            name=config["name"],
            namespaces=config.get("namespaces"),
            schemas=schemas,
        )

    def accepts_request(self, request):
        schema_to_use = None
        for schema in self.schemas:
            try:
                requested_service = schema.get_request_service(request)
                requested_version = schema.get_request_version(request)
                schema_to_use = schema
                break
            except exceptions.CswError:
                logger.debug("Schema {0.namespace} cannot accept "
                             "request".format(schema))
        else:
            logger.debug("Processor {} cannot accept request.".format(self))
        return schema_to_use


class CswContentTypeProcessor(CswRequestProcessor):
    media_type = ""

    def __init__(self, media_type, namespaces=None, schemas=None):
        self.media_type = media_type
        super().__init__(namespaces=namespaces, schemas=schemas)

    def __str__(self):
        return self.media_type

    @classmethod
    def from_config(cls, **config):
        schemas = [CswSchemaProcessor.from_config(**schema_config) for
                   schema_config in config.get("schemas", [])]
        return cls(
            media_type=config["media_type"],
            namespaces=config.get("namespaces"),
            schemas=schemas,
        )


# FIXME - Implement a base class for this one, independent of the CSW service
class CswSchemaProcessor:
    namespace = ""
    type_names = []
    record_mapping = {}
    element_set_names = []

    def __init__(self, namespace, type_names=None, record_mapping=None,
                 element_set_names=None):
        self.namespace = namespace
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


class CswService(base.Service):
    """Base CSW implementation."""
    _name = "CSW"
    distributed_search = CswDistributedSearch()
    operations = []
    content_types = []
    kvp_types = []

    def __init__(self, enabled, distributed_search=None, operations=None,
                 content_types=None, kvp_types=None):
        super().__init__(enabled)
        # load config
        # load eventual plugins
        # lazy load operations
        self.distributed_search = distributed_search or CswDistributedSearch()
        self.operations = operations or []
        self.content_types = content_types or []
        self.kvp_types = kvp_types or []

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

    def accepts_request(self, request):
        """Return True if the incoming request can be processed by this service.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        bool
            Whether this service can process the request or not.

        """

        schema_processor = False
        for processor in (p for p in self.kvp_types + self.content_types):
            logger.debug("Evaluating processor: {}...".format(processor))
            schema_to_use = processor.accepts_request(request)
            if schema_to_use is not None:
                schema_processor = True
                logger.debug("Processor accepts request")
                break
            else:
                logger.debug("Processor cannot accept request")
        else:
            logger.debug("Service {0.identifier} does not accept "
                         "the request".format(self))
        return schema_processor


class Csw202Service(CswService):
    """CSW 2.0.2 implementation."""
    _version = "2.0.2"


class Csw300Service(CswService):
    _version = "3.0.0"
