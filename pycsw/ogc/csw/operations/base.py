"""Base classes for CSW operations"""

from __future__ import absolute_import
import logging

from ....core import util
from ....exceptions import PycswError


LOGGER = logging.getLogger(__name__)


class OperationRequestBase(object):
    name = None  # reimplement in child classes
    allowed_http_methods = (util.HTTP_GET, util.HTTP_POST)
    serializers = []  # reimplement in child classes
    response_base = None  # reimplement in child classes

    def __init__(self, pycsw_server):
        self.pycsw_server = pycsw_server

    @classmethod
    def from_request(cls, pycsw_server, request):
        """Create a new operation object from the input request

        This method will inspect the input request and choose an
        appropriate serializer to use for parsing the request. The serializer
        is chosen from the list of serializers of the class. The first
        serializer that accepts the request's HTTP method and content type
        is selected.

        :param pycsw_server:
        :param request:
        :return:
        """

        # before even trying to create the requested operation class, we can
        # perform content negotiation and be sure that we can create a
        # response using one of the available serializers. So lets check if
        # the requested AcceptFormats are acceptable
        for serializer in cls.serializers:
            try:
                parsed_request = serializer.deserialize(request)
            except PycswError:  # try another serializer from the list
                continue
            else:
                instance = cls(**parsed_request)
                break
        else:  # ran through all serializers and could not parse the request
            raise PycswError(pycsw_server, "", "", "")
        return instance

    def dispatch(self):
        raise NotImplementedError

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def old_dispatch(self, request):
        data_ = request.GET or request.POST or request.body
        validated = self.validate_request(data_)
        return self.process_request(validated)

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def get_serializer(self, cleaned_request):
        result = None
        for response_format in cleaned_request["acceptFormats"]:
            for serializer in self.serializers:
                pass

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def process_request(self, cleaned_request):
        """Process a request

        :arg parameters: The already validated request parameters
        :type parameters: dict
        """
        raise NotImplementedError

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def validate_request(self, data_):
        if isinstance(data_, basestring):
            validated = self.validate_xml(data_)
        else:
            validated = self.validate_kvp(data_)
        return validated

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def validate_http_method(self, method):
        return True if method in self.allowed_http_methods else False

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def validate_kvp(self, parameters):
        """Validate each of the input parameters

        :return: The validated KVP parameters
        :rtype: dict
        :raises: pycsw.exceptions.PycswError
        """
        return {}

    # FIXME - Replace this method with the newer implementation that reliesupon serializers
    def validate_xml(self, request_body):
        """Validate the input request_body

        :return: The validated XML data
        :rtype: etree.Element
        :raises: pycsw.exceptions.PycswError
        """
        return None


class OperationResponseBase(object):

    def __init__(self, pycsw_server):
        self.pycsw_server = pycsw_server

    def serialize(self):
        raise NotImplementedError
