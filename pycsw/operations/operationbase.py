import logging

from .parameters import OperationParameter

logger = logging.getLogger(__name__)


class OperationProcessor:
    """Base class for all CSW operations.

    All CSW operations, including those used by plugins, should adhere to
    the public interface of this base class. This can be achieved by
    inheriting from it and completing the methods that do not have a default
    implementation (you can also duck type your own classes).

    """

    name = ""
    url_path = ""  # used for building URLs for the operation
    _service = None
    enabled = True
    allowed_http_verbs = set()
    constraints = None  # TODO: decide how to implement constraints

    def __init__(self, enabled=True, allowed_http_verbs=None):
        self._service = None
        self.enabled = enabled
        self.allowed_http_verbs = (set(allowed_http_verbs) if
                                   allowed_http_verbs is not None else set())

    def __str__(self):
        return "{0.__class__.__name__}({0.service}, {0.name})".format(self)

    def __call__(self):
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

    @property
    def prepared_parameters(self):
        result = {}
        for param in self.parameters:
            result[param.public_name] = param.__get__(self, self.__class__)
        return result

    def prepare(self, **parameters):
        """Prepare the operation for execution."""
        raise NotImplementedError

