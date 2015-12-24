from __future__ import absolute_import
import logging

from .base import SerializerBase
from ....core import util


LOGGER = logging.getLogger(__name__)


class GetCapabilitiesCsw202Serializer(SerializerBase):
    """A serializer for the GetCapabilities operation request"""

    http_methods = [util.HTTP_GET, util.HTTP_POST]
    input_formats = []
    output_formats = ["text/xml", "application/xml"]

    def parse_request(self, request):
        """
        Version 2.0.2  of the CSW standard states that the GetCapabilities
        request must implement the following parameters:

        * request: has already been parsed by the calling operation
        * service: has already been parsed by the server
        * Sections: will be parsed here
        * AcceptVersions: has already been parsed by the server
        * AcceptFormats: has already been parsed by the calling operation
        * updateSequence: is optional, will be parsed here

        :param request:
        :return:
        """
        params = request.GET if any(request.GET) else request.POST
        parsed = {
            "request": params.get("request"),
            "accept_versions": self._get_list_parameter(params,
                                                        "AcceptVersions"),
            "accept_formats": self._get_list_parameter(params,
                                                       "AcceptFormats"),
            "sections": self._get_list_parameter(params, "Sections"),
            "update_sequence": params.get("updateSequence"),
            "http_accept_headers": request.META["HTTP_ACCEPT"] or ["text/xml"],
        }
        return parsed


class CapabilitiesCsw202Serializer(SerializerBase):
    """A serializer for the Capabilities operation response"""

    output_formats = ["application/xml"]
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"  # TODO: Find a better place for this

    def serialize(self):
        raise NotImplementedError
