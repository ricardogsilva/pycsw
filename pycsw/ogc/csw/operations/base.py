"""Base classes for CSW operations"""

from __future__ import absolute_import
import logging

from ....core import util
from .... import exceptions


LOGGER = logging.getLogger(__name__)

class CswOperationBase(object):
    serializers = []

    def __init__(self, csw_version_interface):
        self.csw_version_interface = csw_version_interface


class OperationRequestBase(CswOperationBase):
    # reimplement these class attributes in derived classes
    allowed_http_methods = (util.HTTP_GET, util.HTTP_POST)
    response_base = None

    @classmethod
    def from_request(cls, csw_version_interface, request):
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

        for serializer in cls.serializers:
            try:
                parsed_request = serializer.deserialize(request)
            except exceptions.PycswError:  # try another serializer from the list
                continue
            else:
                instance = cls(csw_version_interface, **parsed_request)
                break
        else:  # ran through all serializers and could not parse the request
            raise exceptions.PycswError(
                code=exceptions.OPERATION_NOT_SUPPORTED)
        return instance

    def dispatch(self):
        raise NotImplementedError


class OperationResponseBase(CswOperationBase):

    def serialize(self):
        raise NotImplementedError
