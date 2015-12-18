"""Base CSW class"""

from __future__ import absolute_import

from ...core import util
from ...exceptions import PycswError


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
            name = request.GET.get("request", request.POST["request"])
        except KeyError:
            for op, op_class_path in self.operations.items():
                if request.body.find(op.name) != -1:
                    name = op
                    break
            else:  # for loop ran until the end, we have no operation
                # FIXME: look up the proper values for the exception
                raise PycswError(self.parent, None, None, None)
        operation_class_path = self.operations[name]
        module_path, _, class_name = operation_class_path.rpartition(".")
        operation_class = util.lazy_import_dependency(module_path,
                                                      class_name)
        operation = operation_class.from_request(self.parent, request)
        return operation.dispatch()
        #operation = operation_class(self.parent)
        #if operation.validate_http_method(request.method):
        #    result = operation.process_request(request)
        #else:
        #    # FIXME: look up the proper values for the exception
        #    raise PycswError(self.parent, None, None, None)
        #return result
