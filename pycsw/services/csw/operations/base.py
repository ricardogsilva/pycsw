from lxml import etree

from ....httprequest import HttpVerb

class CswOperation:
    """Base class for all CSW operations.

    All CSW operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    """

    _service = "CSW"
    _version = ""
    enabled = False
    # TODO: CSW operations should accept multiple content-types
    #     These content-types will be used to parse the request's parameters
    # TODO: CSW operations should accept multiple schemas for each content-type
    #     These schemas are different ways to encode the request's parameters
    # TODO: CSW operations should also respond with multiple content-types
    # TODO: The response's content-types should also use different schemas
    # TODO: It should be possible to extend request and response content-types
    #     and schemas via plugins


    def __init__(self, enabled=True):
        self.enabled = enabled

    def process_request(self, request):
        raise NotImplementedError

    def can_process_request(self, request):
        test_function = {
            HttpVerb.GET: self._can_process_get_request,
            HttpVerb.POST: self._can_process_post_request,
        }.get(request.method)
        return test_function(request)

    def _can_process_get_request(self, request):
        service_ok = request.parameters.get("service") == self._service
        version_ok = request.parameters.get("version") == self._version
        return service_ok and version_ok

    def _can_process_post_request(self, request):
        if request.exml:
            service_ok = request.exml.get("service") == self._service
            version_ok = request.exml.get("version") == self._version
            result = service_ok and version_ok
        else:
            result = False
        return result


class GetCapabilities202Operation(CswOperation):
    _name = "GetCapabilities"
    _version = "2.0.2"

    def process_request(self, request):
        pass

    def _can_process_get_request(self, request):
        service_ok = request.parameters.get("service") == self._service
        version_ok = request.parameters.get("version") == self._version
        if not version_ok:
            # GetCapabilities requests may not have a 'version' parameter
            version_ok = request.parameters.get("request") == self._name
        return service_ok and version_ok

    def _can_process_post_request(self, request):
        if request.exml:
            service_ok = request.exml.get("service") == self._service
            version_ok = request.exml.get("version") == self._version
            if not version_ok:
                # GetCapabilities requests do not have a 'version' parameter
                version_ok = etree.QName(request.exml).localname == self._name
            result = service_ok and version_ok
        else:
            result = False
        return result
