"""Base CSW class"""

from __future__ import absolute_import

from ...core import util
from ... import exceptions


class CswInterface(object):
    version = None  # re-assign in child classes
    operations = dict()
    pycsw_server = None

    def __init__(self, pycsw_server=None):
        self.pycsw_server = pycsw_server

    def dispatch(self, request):
        try:
            name = request.GET.get("request") or request.POST["request"]
        except KeyError:
            for op_name, op_class_path in self.operations.items():
                if request.body.find(op_name) != -1:
                    name = op_name
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
            operation = operation_class.from_request(self, request)
            return operation.dispatch()
