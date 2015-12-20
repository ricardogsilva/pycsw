"""Base CSW class"""

from __future__ import absolute_import

from ...core import util
from ... import exceptions


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
        try:
            name = request.GET.get("request", request.POST["request"])
        except KeyError:
            for op, op_class_path in self.operations.items():
                if request.body.find(op.name) != -1:
                    name = op
                    break
            else:  # for loop ran until the end, we have no operation
                raise exceptions.PycswError(
                    code=exceptions.NO_APPLICABLE_CODE)
        try:
            operation_class_path = self.operations[name]
        except KeyError:
            raise exceptions.PycswError(
                code=exceptions.OPERATION_NOT_SUPPORTED,
                locator=name
            )
        else:
            module_path, _, class_name = operation_class_path.rpartition(".")
            operation_class = util.lazy_import_dependency(module_path,
                                                          class_name)
            operation = operation_class.from_request(self.parent, self,
                                                     request)
            return operation.dispatch()
