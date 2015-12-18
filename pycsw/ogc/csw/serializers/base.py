"""Operation serializers for CSW operations"""

from __future__ import absolute_import
import logging

from ....exceptions import PycswError


LOGGER = logging.getLogger(__name__)


class SerializerBase(object):
    http_methods = []
    input_formats = []
    output_formats = []
    output_schema = None

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, request):
        if request.method not in self.http_methods:
            raise PycswError("", "", "Invalid Http method")
        if (any(self.input_formats) and
                    request.content_type not in self.input_formats):
            raise PycswError("", "", "Invalid ContentType")
        return self.parse_request(request)

    def parse_request(self, request):
        raise NotImplementedError
