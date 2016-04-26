"""Operation parameter classes for pycsw."""


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
        self.storage_name = "_{}#{}".format(_prefix, index)
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
            result = getattr(instance, self.storage_name)
        return result

    def __set__(self, instance, value):
        validated = self.validate(value)
        setattr(instance, self.storage_name, validated)

    def validate(self, value):
        raise NotImplementedError


class IntParameter(OperationParameter):

    def validate(self, value):
        if self.optional and value is None:
            result = self.default
        else:
            possible = int(value)
            if (possible in self.allowed_values or
                        len(self.allowed_values) == 0):
                result = possible
            else:
                raise ValueError
        return result


class TextParameter(OperationParameter):

    def validate(self, value):
        if self.optional and value is None:
            result = self.default
        else:
            possible = str(value)
            if len(self.allowed_values) == 0:
                result = possible
            elif possible in self.allowed_values:
                result = possible
            else:
                raise ValueError("Value {} is not allowed".format(possible))
        return result


class BooleanParameter(OperationParameter):

    def validate(self, value):
        if self.optional and value is None:
            result = self.default
        elif not self.optional and value is None:
            raise ValueError("Value is mandatory")
        else:
            result = bool(value)
        return result


class TextListParameter(OperationParameter):

    def validate(self, values):
        list_values = list(values) if values is not None else []
        if self.optional and len(list_values) == 0:
            result = list(self.default)
        else:
            result = []
            for possible_value in (str(v) for v in list_values):
                if len(self.allowed_values) == 0:
                    result.append(possible_value)
                elif possible_value in self.allowed_values:
                    result.append(possible_value)
                else:
                    raise ValueError("Value {} is not "
                                     "allowed".format(possible_value))
        return result


