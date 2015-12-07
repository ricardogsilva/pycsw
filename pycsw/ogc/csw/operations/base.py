"""Base classes for CSW operations"""

from __future__ import absolute_import
import logging

from ....core import util

LOGGER = logging.getLogger(__name__)


class OperationBase(object):
    name = None  # reimplement in child classes
    allowed_http_methods = (util.HTTP_GET, util.HTTP_POST)

    def __init__(self, pycsw_server):
        self.pycsw_server = pycsw_server

    def process_request(self, request):
        data_ = request.GET or request.POST or request.body
        if isinstance(data_, basestring):
            validated_element = self.validate_xml(data_)
            self.process_xml_request(validated_element)
        else:
            validated_kvp = self.validate_kvp(data_)
            self.process_kvp_request(validated_kvp)

    def process_kvp_request(self, parameters):
        """Process a request that is encoded as KVP parameters

        Reimplement this method in a child class if the class accepts KVP
        requests.

        :arg parameters: The already validated request KVP parameters
        :type parameters: dict
        """
        raise NotImplementedError

    def process_xml_request(self, request_element):
        """Process a request that is encoded as an XML document

        Reimplement this method in a child class if the class accepts XML
        requests.

        :arg request_element: The already validated request XML
        :type request_element: etree.Element
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

