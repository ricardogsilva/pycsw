import logging

from lxml import etree

from pycsw.services import base
from pycsw.httprequest import HttpVerb

logger = logging.getLogger(__name__)


class CswService(base.Service):
    """Base CSW implementation."""
    _name = "CSW"
    operations = []

    def __init__(self, enabled, **configuration_keys):
        super().__init__(enabled)
        # load config
        # load eventual plugins
        # lazy load operations
        pass

    def _configure_distributed_search(self, **configuration_keys):
        config = configuration_keys.get("distributed_search", {})
        if config.get("enabled", False):
            # load the rest of the config
            pass
        else:
            pass  # do not enable distributed search

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
