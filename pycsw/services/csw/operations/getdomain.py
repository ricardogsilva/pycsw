"""GetDomain operation of the CSW standard."""

import logging

from .... import parameters
from ....operationbase import Operation

logger = logging.getLogger(__name__)

class GetDomain(Operation):
    """GetDomain operation.

    This operation needs to know about all of the parameters that are
    available in each of its Service's operations. As such, upon initialization
    it will load all other operations.

    """

    name = "GetDomain"
    parameter_name = parameters.TextListParameter("ParameterName",
                                                  optional=True)
    property_name = parameters.TextListParameter("PropertyName", optional=True)
    test = parameters.IntParameter("MyParameter", default=0,
                                   allowed_values=range(10), optional=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._update_parameter_name()

    @property
    def service(self):
        return super().service

    @service.setter
    def service(self, new_service):
        self._service = new_service
        self._update_parameter_name()

    def _update_parameter_name(self):
        logger.debug("_update_parameter_name called")
        existing_parameter_names = ["{0}.{1}".format(self.name,
                                                     param.public_name) for
                                    param in self.parameters]
        if self.service is not None:
            for operation in (op for op in self.service.operations if
                              op is not self):
                op_params = ["{0}.{1}".format(operation.name,
                                              param.public_name) for param
                             in operation.parameters]
                existing_parameter_names.extend(op_params)
            #for op in self.service.operations:
            #    if op is not self:  # do not repeat own parameters
            #        op_params = ["{0}.{1}".format(op.name, param.public_name)
            #                     for param in op.parameters]
            #        existing_parameter_names.extend(op_params)
            print("existing_parameter_names: {}".format(existing_parameter_names))
        self.__class__.parameter_name.allowed_values = existing_parameter_names
        logger.debug("setting parameter_name...")
        self.parameter_name = existing_parameter_names
