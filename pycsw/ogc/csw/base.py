"""Base CSW class"""

from __future__ import absolute_import
from collections import namedtuple

from ...core import util
from ...exceptions import PycswError


CswOperationSpecification = namedtuple(
    "CswOperationSpecification",
    ["name", "allowed_http_methods", "handler"]
)


class CswInterface(object):
    version = None  # re-assign in child classes

    def __init__(self, pycsw_server):
        self.parent = pycsw_server
        self.operations = {
            util.CSW_OPERATION_GET_CAPABILITIES: ("pycsw.ogc.csw.operations."
                                                  "getcapabilities."
                                                  "GetCapabilities"),
            util.CSW_OPERATION_GET_RECORDS: ("pycsw.ogc.csw.operations."
                                             "getrecords.GetRecords"),
        }

    def dispatch(self, request):
        result = None
        try:
            name = request.GET["request"]
            operation_class_path = self.operations[name]
        except KeyError:
            try:
                name = request.POST["request"]
                operation_class_path = self.operations[name]
            except KeyError:
                for op, op_class_path in self.operations.items():
                    if request.body.find(op.name) != -1:
                        operation_class_path = op_class_path
                        break
                else:  # for loop ran until the end, we have no operation
                    # FIXME: look up the proper values for the exception
                    raise PycswError(self.parent, None, None, None)
        module_path, _, class_name = operation_class_path.rpartition(".")
        operation_class = util.lazy_import_dependency(module_path,
                                                      class_name)
        operation = operation_class(self.parent)
        if operation.validate_http_method(request.method):
            result = operation.process_request(request)
        else:
            # FIXME: look up the proper values for the exception
            raise PycswError(self.parent, None, None, None)
        return result
