from __future__ import absolute_import
import logging

from .base import SerializerBase
from ....core import util


LOGGER = logging.getLogger(__name__)


class GetCapabilitiesCsw202Serializer(SerializerBase):
    """A serializer for the GetCapabilities operation request"""

    http_methods = [util.HTTP_GET, util.HTTP_POST]
    input_formats = []

    def parse_request(self, request):
        """
        Version 2.0.2  of the CSW standard states that the GetCapabilities
        request must implement the following parameters:

        * service: has already been parsed by the server
        * AcceptVersions: has already been parsed by the server
        * request: has already been parsed by the calling operation
        * Sections: will be parsed here
        * AcceptFormats: will be parsed here

        :param request:
        :return:
        """

        result = {
            "ServiceIdentification": None,
            "ServiceProvider": None,
            "OperationsMetadata": None,
            "Filter_Capabilities": None,
        }
        return request


class CapabilitiesCsw202Serializer(SerializerBase):
    """A serializer for the Capabilities operation response"""

    output_formats = ["application/xml"]
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"  # TODO: Find a better place for this

    def serialize(self):
        raise NotImplementedError
