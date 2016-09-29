"""Operation parameter classes for pycsw.

Parameters and constraints
---------------------------

Both services and operations have parameters and constraints.

* Parameter - A value that can be set by the client code at runtime. It may
  have a fixed set of allowed values.

  Examples:

      The version of a service is a server parameter. Client code can choose
      which version of a given service it wants to use;

      The elementsetname of a CSW GetRecords operation is an operation
      parameter. Client code can choose a value from a set of predefined
      values;

* Constraint - Constraint on valid domain of a non-parameter quantity.
  Constraints represent configuration values of the server and cannot be
  changed at runtime;

  Examples:

      The set of catalogues that are federated with a given CSW instance
      is configured by the server's admin and cannot be changed by the user;

"""

from pycsw.exceptions import CswError
from pycsw.exceptions import INVALID_PARAMETER_VALUE


class OperationParameter:
    __counter = 0

    def __init__(self, public_name, optional=False, allowed_values=None,
                 metadata=None, default=None):
        """A descriptor class for managing operation parameters.

        Parameters
        ----------
        public_name: str
            The public name of the parameter
        optional: bool, optional
            Whether the parameter is optional or mandatory
        allowed_values: list
            Values that the parameter can have
        metadata: str
            Additional information about the parameter

        """

        _prefix = self.__class__.__name__
        index = self.__class__.__counter
        self.storage_name = "_{0}#{1}".format(_prefix, index)
        self.__class__.__counter += 1
        self.public_name = public_name
        self.optional = optional
        self.allowed_values = (list(allowed_values) if
                               allowed_values is not None else [])
        self.metadata = metadata
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            result = self
        else:
            possible = getattr(instance, self.storage_name)
            result = possible if possible is not None else self.default
        return result

    def __set__(self, instance, value):
        if value is not None:
            validated = self.validate(value)
        setattr(instance, self.storage_name, validated)

    def validate(self, value):
        raise NotImplementedError


class IntParameter(OperationParameter):

    def __init__(self, *args, default=0, **kwargs):
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value):
        possible = int(value)
        if (possible in self.allowed_values or len(self.allowed_values) == 0):
            result = possible
        else:
            raise ValueError("Value {0!r} is not allowed".format(value))
        return result


class TextParameter(OperationParameter):

    def __init__(self, *args, default="", **kwargs):
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value):
        possible = str(value)
        if len(self.allowed_values) == 0:
            result = possible
        elif possible in self.allowed_values:
            result = possible
        else:
            raise ValueError("Value {0!r} is not allowed".format(possible))
        return result


class BooleanParameter(OperationParameter):

    def __init__(self, *args, default=False, **kwargs):
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value):
        result = bool(value)
        return result


class TextListParameter(OperationParameter):

    def __init__(self, *args, default=False, **kwargs):
        default = default or []
        super().__init__(*args, default=default, **kwargs)

    def validate(self, value):
        list_values = list(value)
        result = []
        for possible_value in (str(v) for v in list_values):
            if len(self.allowed_values) == 0:
                result.append(possible_value)
            elif possible_value in self.allowed_values:
                result.append(possible_value)
            else:
                raise ValueError("Value {0!r} is not "
                                 "allowed".format(possible_value))
        return result
