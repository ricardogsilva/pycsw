"""Content-type handlers for pycsw."""

import logging

from ..exceptions import PycswError
from ..exceptions import NO_APPLICABLE_CODE
from . import util
from . import etree


LOGGER = logging.getLogger(__name__)

# pycsw.ogc.csw.csw202.Csw202Mode must feature:
# * a set of serializer classes
# * a set of operations

class KvpHandler(object):
    name = "kvp"
    http_content_types = ["application/x-www-form-urlencoded"]
    operation_modes = {
        "csw202": ["pycsw.ogc.serializers.csw202.Csw202Serializer"],
        "csw300": ["pycsw.ogc.serializers.csw300.Csw300Serializer"],
        "sru": [],
        "opensearch": [],
    }

    def get_request_data(self, request):
        if request.method == util.HTTP_GET:
            request_data = request.GET
        elif request.method == util.HTTP_POST:
            content_type = request.META.get("HTTP_CONTENT_TYPE")
            if content_type in self.http_content_types:
                request_data = request.POST
            else:  # invalid content_type
                raise PycswError(NO_APPLICABLE_CODE)
        else:  # invalid http method
            raise PycswError(NO_APPLICABLE_CODE)
        return request_data

    def get_operation_mode(self, request_data):
        requested = request_data.get("mode", util.CSW_SERVICE).upper()
        try:
            mode = {m.name: m for m in self.operation_modes}[requested]
        except KeyError:
            raise PycswError(NO_APPLICABLE_CODE)
        else:
            return mode

    def get_request_parameters(self, request_data, operation_mode):
        pass

    # verify that the content-type is correct
    # extract request data
    # verify that the operation mode is correct
    # get the serializer and extract requested parameters
    # instantiate the correct operation for the requested mode
    # dispatch the request and return the response


def get_kvp_data(request):
    http_content_types = ["application/x-www-form-urlencoded"]
    if request.method == util.HTTP_GET:
        request_data = request.GET
    elif request.method == util.HTTP_POST:
        content_type = request.META.get("HTTP_CONTENT_TYPE")
        if content_type in http_content_types:
            request_data = request.POST
        else:  # invalid content_type
            raise PycswError(NO_APPLICABLE_CODE)
    else:  # invalid http method
        raise PycswError(NO_APPLICABLE_CODE)
    operation_mode = request_data.get("mode", "csw").lower()
    return request_data, operation_mode


def get_xml_data(request):
    http_content_types = ["application/xml", "text/xml"]
    # hardcoded for now, in the future we may support other modes
    # with XML encoding
    operation_mode = "csw"
    is_post = request.method == util.HTTP_POST
    content_type = request.META.get("HTTP_CONTENT_TYPE")
    content_allowed = content_type in http_content_types
    if is_post and content_allowed:
        try:
            xml_element = etree.etree.fromstring(
                    request.body, parser=etree.validating_parser)
        except Exception:  # FIXME: catch a more specific exception
            # invalid XML
            raise PycswError(NO_APPLICABLE_CODE)
        else:
            request_data = xml_element
    else:
        raise PycswError(NO_APPLICABLE_CODE)
    return request_data, operation_mode


# TODO: delete this code if the class based approach is indeed unnecessary
#class KvpContentType(object):
#
#    http_content_types = ["application/x-www-form-urlencoded"]
#    operation_modes = []
#
#
#    def __init__(self, request):
#        if request.method == util.HTTP_GET:
#            self.request_data = request.GET
#        elif request.method == util.HTTP_POST:
#            content_type = request.META.get("HTTP_CONTENT_TYPE")
#            if content_type in self.http_content_types:
#                self.request_data = request.POST
#            else:  # invalid content_type
#                raise PycswError(NO_APPLICABLE_CODE)
#        else:  # invalid http method
#            raise PycswError(NO_APPLICABLE_CODE)
#       self.operation_mode = self.request_data.get("mode", "csw").lower()



#class XmlContentType(object):
#
#    http_content_types = ["application/xml", "text/xml"]
#    # hardcoded for now, in the future we may support other modes
#    # with XML encoding
#    operation_mode = "csw"
#
#    def __init__(self, request):
#        is_post = request.method == util.HTTP_POST
#        content_type = request.META.get("HTTP_CONTENT_TYPE")
#        content_allowed = content_type in self.http_content_types
#        if is_post and content_allowed:
#            try:
#                xml_element = etree.etree.fromstring(
#                    request.body, parser=etree.validating_parser)
#            except Exception:  # FIXME: catch a more specific exception
#                # invalid XML
#                raise PycswError(NO_APPLICABLE_CODE)
#            else:
#                self.request_data = xml_element
#        else:
#            raise PycswError(NO_APPLICABLE_CODE)
