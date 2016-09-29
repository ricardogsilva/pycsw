"""Base classes for pycsw operations.

The proposed interaction is something like:

* Instantiate a new operation
* Call the `set_parameter_values` method with the parameter names and values
  that have been parsed by the appropriate request_parser object
* Call the operation and obtain its result
* Pass the result over to the appropriate response_renderer object

"""

import logging

from .parameters import OperationParameter

logger = logging.getLogger(__name__)


class Operation:
    """Base class for all pycsw operations.

    All operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    Operations must have:

    * a name;
    * a set of HTTP verbs that can be used to invoke it;
    * a URL path informing how the operation can be called

    Operations may have:

    * Constraints, which are set server side, with values from the code or
      from the configuration. These values constrain what the operation can
      do;

    * Parameters, which can set by clients. Parameters may be optional or
      mandatory and they may have a range of allowed values. These values
      represent the way the client wants to call the operation;

    The information on constraints and parameters is used by the
    GetCapabilities operation of the service to reveal what the service
    can do.

    """

    name = ""  # must be reimplemented in child classes
    url_path = ""  # used for building URLs for the operation
    enabled = True
    allowed_http_verbs = set()

    service = None  # set by the container that manages services

    def __init__(self, enabled=True, allowed_http_verbs=None, **kwargs):
        self.service = None
        self.enabled = enabled
        self.allowed_http_verbs = (set(allowed_http_verbs) if
                                   allowed_http_verbs is not None else set())
        # initialize parameters with they're default values
        for param in self.parameters:
            setattr(self, param.storage_name, param.default)
        # eventually update parameters with input kwargs
        for arg, value in kwargs.items():
            setattr(self, arg, value)

    def __str__(self):
        return "{0.__class__.__name__}({0.service}, {0.name})".format(self)

    def __call__(self):
        """Perform the main task of the operation.

        Reimplement this method in derived classes.

        """

        raise NotImplementedError

    @property
    def parameters(self):
        result = []
        for attribute in self.__class__.__dict__.values():
            if isinstance(attribute, OperationParameter):
                result.append(attribute)
        return result

    def set_parameter_values(self, **kwargs):
        """Update the value of an operation's parameters.

        This method should be called in order to update an operation's
        parameters. Direct manipulation of a parameter's value is not
        recommended because usually the client code will reference parameters
        by they're public name, which is not the same as the name that the
        parameters have as instance attributes.

        Raises
        ------
        RuntimeError
            If one of the input parameter names is not valid

        """

        for public_name, value_to_set in kwargs.items():
            try:
                param = [p for p in self.parameters if
                         p.public_name == public_name][0]
            except IndexError:
                raise RuntimeError("Invalid parameter: {0}".format(public_name))
            else:
                param.__set__(self, value_to_set)

    def get_parameter_domain(self, public_name):
        """Retrieve the domain of an input parameter.

        .. note::

           This method belongs to a CSW specific base operation, not on the
           main base. Operations from other services need not define this
           method.

        This method is called by the GetDomain operation in order to gather
        information on each parameter of an operation.

        Parameters
        ----------
        public_name: str
            The public name of the parameter to operate on.

        Returns
        -------
        list
            The domain of the requested parameter.

        """

        try:
            param = [p for p in self.parameters if
                     p.public_name == public_name][0]
        except IndexError:
            raise RuntimeError("Invalid parameter: {0!r}".format(public_name))
        else:
            return param.allowed_values

