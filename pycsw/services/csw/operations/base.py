from lxml import etree

from ....httprequest import HttpVerb

class CswOperation:
    """Base class for all CSW operations.

    All CSW operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    """

    _name = ""
    _version = ""
    enabled = False
    allowed_http_verbs = {}


    def __init__(self, enabled=True, allowed_http_verbs=None):
        self.enabled = enabled
        self.allowed_http_verbs = {
            HttpVerb.GET: self.parse_get_request,
            HttpVerb.POST: self.parse_post_request,
        }.update(allowed_http_verbs or {})

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @classmethod
    def from_config(cls, **config):
        http_verbs = [HttpVerb[v] for v in config.get("allowed_http_verbs", [])]
        return cls(
            enabled=config.get("enabled", True),
            allowed_http_verbs=http_verbs,
        )

    def process_request(self, *args, **kwargs):
        raise NotImplementedError

    def parse_get_request(self, request, service):
        """Validate request and extract operation parameters.

        Parameters
        ----------
        request: PycswHttpRequest
            The input request, as received by the service instance.

        Returns
        -------
        dict
            A mapping with the keyword parameters that should be passed to the
            `process_request` method.

        Raises
        ------
        CswException
            If the request is not valid.
        """
        raise NotImplementedError

    def parse_post_request(self, request):
        raise NotImplementedError


class GetCapabilities202Operation(CswOperation):
    _name = "GetCapabilities"
    _version = "2.0.2"

    def process_request(self, request, service, sections, accept_versions,
                        accept_formats, update_sequence=None):
        pass

    def parse_get_request(self, request, *args, **kwargs):
        raise NotImplementedError
