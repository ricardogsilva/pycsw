"""Operation serializers for CSW operations"""

from __future__ import absolute_import
import logging

from .... import exceptions


LOGGER = logging.getLogger(__name__)


class SerializerBase(object):
    http_methods = []
    input_formats = []
    output_formats = []
    output_schema = None

    def parse_request(self, request):
        """Parse an incoming request.

        The request must be parsed into a mapping that can then be fed to
        the appropriate operation class' `__init__`.

        Reimplement this method in derived classes.

        :param request:
        :return:
        """
        raise NotImplementedError

    def serialize(self):
        # reimplement this method in derived classes
        raise NotImplementedError

    def deserialize(self, request):
        # validate general constraints:
        if request.method not in self.http_methods:
            raise exceptions.PycswError(code=exceptions.NO_APPLICABLE_CODE)
        elif any(self.input_formats) and (request.content_type not in
                                          self.input_formats):
            raise exceptions.PycswError(code=exceptions.NO_APPLICABLE_CODE)
        else:  # parse the request
            return self.parse_request(request)

    def _get_list_parameter(self, parameters, name):
        parsed = []
        for item in parameters.get(name, "").split(","):
            if item != "":
                parsed.append(item.strip())
        return parsed
