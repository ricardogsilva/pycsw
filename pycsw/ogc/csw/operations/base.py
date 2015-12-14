"""Base classes for CSW operations"""

from __future__ import absolute_import
import logging

from ....core import util

LOGGER = logging.getLogger(__name__)


class OperationRequestBase(object):
    name = None  # reimplement in child classes
    allowed_http_methods = (util.HTTP_GET, util.HTTP_POST)

    def __init__(self, pycsw_server):
        self.pycsw_server = pycsw_server

    def dispatch(self, request):
        data_ = request.GET or request.POST or request.body
        if isinstance(data_, basestring):
            validated = self.validate_xml(data_)
        else:
            validated = self.validate_kvp(data_)
        return self.process_request(validated)

    def process_request(self, cleaned_request):
        """Process a request

        :arg parameters: The already validated request parameters
        :type parameters: dict
        """
        raise NotImplementedError

    def validate_http_method(self, method):
        return True if method in self.allowed_http_methods else False

    def validate_kvp(self, parameters):
        """Validate each of the input parameters

        :return: The validated KVP parameters
        :rtype: dict
        :raises: pycsw.exceptions.PycswError
        """
        return {}

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
