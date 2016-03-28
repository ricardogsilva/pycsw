import logging

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""

    def __init__(self, enabled):
        self.enabled = enabled

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

    def accepts_request(self, request):
        """Find out if the incoming request can be processed by this service.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.csw.csw.CswSchemaProcessor
            The schema processor object that can process the request.

        """

        raise NotImplementedError

