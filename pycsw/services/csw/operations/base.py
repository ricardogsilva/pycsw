import logging

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
    enabled = False
    allowed_http_verbs = None


    def __init__(self, enabled=True, allowed_http_verbs=None):
        self._service = None
        self.enabled = enabled
        self.allowed_http_verbs = (list(allowed_http_verbs) if
                                   allowed_http_verbs is not None else [])

    @property
    def name(self):
        return self._name

    @property
    def service(self):
        return self._service


class GetCapabilities202Operation(CswOperation):
    _name = "GetCapabilities"

    def __call__(self, sections, accept_versions, accept_formats,
                 update_sequence=None):
        logger.debug("{0.__class__.__name__} called".format(self))

