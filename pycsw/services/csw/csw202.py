from . import cswbase
from ...exceptions import CswError
from ...exceptions import PycswError
from ...exceptions import INVALID_PARAMETER_VALUE


class Csw202Service(cswbase.CswService):
    """CSW 2.0.2 implementation."""
    _version = "2.0.2"

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

