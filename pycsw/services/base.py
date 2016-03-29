import logging

logger = logging.getLogger(__name__)


class ServiceContainer:
    """A container for services."""

    def __init__(self, pycsw_server=None):
        self.pycsw_server = pycsw_server
        self._container = []

    def __iter__(self):  # making objects iterable
        return iter(self._container)

    def __getitem__(self, item):  # implementing the sequence protocol
        return self._container[item]

    def __len__(self):  # implementing the sequence protocol
        return len(self._container)

    def append(self, service):
        self._container.append(service)
        service.server = self.pycsw_server

    def insert(self, index, service):
        self._container.insert(index, service)
        service.server = self.pycsw_server

    def pop(self):
        service = self._container.pop()
        service.server = None
        return service

    def remove(self, service):
        try:
            self._container.remove(service)
            service.server = None
        except ValueError:
            raise


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""
    _server = None

    def __init__(self, enabled, server=None):
        self.enabled = enabled
        self._server = server

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, new_server):
        old_server = self._server
        if old_server is not None:
            old_server.services.remove(self)
        if new_server is not None:
            new_server.services.append(self)
        else:
            self._server = new_server

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

    def accepts_request(self, request):
        """Find out if the incoming request can be processed by this service.

        Reimplement this method in child classes.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        pycsw.services.csw.cswbase.CswSchemaProcessor
            The schema processor object that can process the request.

        """

        raise NotImplementedError

