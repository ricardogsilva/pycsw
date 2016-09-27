import logging

from .parameters import OperationParameter
from . import parameters

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

    _service = None  # set by the container that manages services

    def __init__(self, enabled=True, allowed_http_verbs=None, **kwargs):
        self._service = None
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
    def service(self):
        return self._service

    @property
    def parameters(self):
        result = []
        for attribute in self.__class__.__dict__.values():
            if isinstance(attribute, OperationParameter):
                result.append(attribute)
        return result

    #@property
    #def prepared_parameters(self):
    #    result = {}
    #    for param in self.parameters:
    #        result[param.public_name] = param.__get__(self, self.__class__)
    #    return result

    #def prepare(self, **parameters):
    #    """Prepare the operation for execution."""
    #    raise NotImplementedError

