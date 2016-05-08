from . import cswbase
from ...exceptions import CswError
from ...exceptions import PycswError
from ...exceptions import INVALID_PARAMETER_VALUE


class Csw202Service(cswbase.CswService):
    """CSW 2.0.2 implementation."""
    _version = "2.0.2"

    def __init__(self, title="", abstract="", keywords=None, fees="",
                 access_constraints="", repository=None,
                 distributed_search=None):
        super().__init__(title=title, abstract=abstract, keywords=keywords,
                         fees=fees, access_constraints=access_constraints,
                         repository=repository,
                         distributed_search=distributed_search)
        self.namespaces = {
            "csw": "http://www.opengis.net/cat/csw/2.0.2",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "ows": "http://www.opengis.net/ows",

        }
        self.title = "Dummy CSW title"
        self.abstract = "Dummy abstract"
        self.keywords = ["dummy1", "dummy2"]
        self.fees = "Dummy fees"
        self.access_constraints = "Dummy access constraints"

    def get_renderer(self, operation, request):
        for renderer in self.response_renderers:
            if renderer.can_render(operation=operation, request=request):
                result = renderer
                break
        else:
            # TODO: add specific CSW exceptions for other operations that
            # have an outputFormat parameter
            if operation.name == "GetCapabilities":
                raise CswError(code=INVALID_PARAMETER_VALUE,
                               locator="AcceptFormats")
            else:
                raise PycswError()
        return result

