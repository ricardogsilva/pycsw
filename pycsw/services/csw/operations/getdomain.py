"""GetDomain operation of the CSW standard."""

import logging

from .... import parameters
from ....operationbase import Operation

logger = logging.getLogger(__name__)

class GetDomain(Operation):
    """GetDomain operation.

    This operation needs to know about all of the parameters that are
    available in each of its Service's operations.

    """

    name = "GetDomain"
    parameter_name = parameters.TextListParameter(
        "ParameterName",
        optional=True,
        allowed_values=["GetDomain.ParameterName", "GetDomain.PropertyName"],
        default=["GetDomain.ParameterName", "GetDomain.PropertyName"]
    )
    property_name = parameters.TextListParameter(
        "PropertyName",
        optional=True
    )

    def __call__(self):
        """Execute the GetDomain operation."""
        self.update_allowed_parameter_names()
        param_domains = dict()
        for param in self.parameter_name:
            # at this point we know that params have already been validated
            # so they are legal, no need to recheck
            op_name, param_name = param.split(".")
            operation = [op for op in self.service.operations if
                         op.name == op_name][0]
            domain = operation.get_parameter_domain(param_name)
            param_domains[param] = domain
        return param_domains

    def set_parameter_values(self, **kwargs):
        if "ParameterName" in kwargs.keys():
            self.update_allowed_parameter_names()
        super().set_parameter_values(**kwargs)

    def update_allowed_parameter_names(self):
        """Get the allowed values for the 'ParameterName' parameter.

        The 'ParameterName' parameter holds the names of all operation
        parameters that are currently available in the service.

        """

        existing_parameter_names = ["{0}.{1}".format(self.name,
                                                     param.public_name) for
                                    param in self.parameters]
        if self.service is not None:
            for op in self.service.operations:
                if op is not self:  # do not repeat own parameters
                    op_params = ["{0}.{1}".format(op.name, param.public_name)
                                 for param in op.parameters]
                    existing_parameter_names.extend(op_params)
        self.__class__.parameter_name.allowed_values = existing_parameter_names
