import logging

from lxml import etree

from pycsw.services import base
from pycsw.httprequest import HttpVerb

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


class CswContentTypeProcessor:
    media_type = ""
    namespaces = {}
    accepted_schemas = []

    def __init__(self, media_type, namespaces=None, accepted_schemas=None):
        self.media_type = media_type
        self.namespaces = namespaces or {}
        self.accepted_schemas = accepted_schemas or []

    @classmethod
    def from_config(cls, **config):
        schemas = [CswSchemaProcessor.from_config(**schema_config) for
                   schema_config in config.get("schemas", [])]
        return cls(
            media_type=config["media_type"],
            namespaces=config.get("namespaces"),
            accepted_schemas=schemas,
        )


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

    def __init__(self, enabled, distributed_search=None, operations=None,
                 content_types=None):
        super().__init__(enabled)
        # load config
        # load eventual plugins
        # lazy load operations
        self.distributed_search = distributed_search or CswDistributedSearch()
        self.operations = operations or []
        self.content_types = content_types or []

    @classmethod
    def from_config(cls, **config):
        distributed_search = CswDistributedSearch.from_config(
            **config.get("distributed_search", {}))
        content_types = [CswContentTypeProcessor.from_config(**c) for c
                         in config.get("content_types", [])]
        return cls(
            enabled=config.get("enabled", False),
            distributed_search=distributed_search,
            content_types=content_types,
        )

    @property
    def enabled_operations(self):
        return (op for op in self.operations if op.enabled)

    def get_requested_operation(self, request):
        """Return True if the request can be processed by this service."""
        for op in self.enabled_operations:
            if op.can_process_request(request):
                operation = op
                break
        else:
            operation = None
        return operation

    def _operation_enabled(self, operation_name):
        """Return True if the operation is enabled."""
        return operation_name in [op.name for op in self.enabled_operations]



class Csw202Service(CswService):
    """CSW 2.0.2 implementation

    Examples
    --------

    >>> service = Csw202Service()
    >>> operation = service.get_requested_operation(request)
    >>> response = operation.process_request(request)

    """
    _version = "2.0.2"


class Csw300Service(CswService):
    _version = "3.0.0"
