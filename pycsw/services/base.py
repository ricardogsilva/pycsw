import logging

logger = logging.getLogger(__name__)


class Service:
    """Base class for all pycsw services."""

    _name = ""
    _version = ""

    def __init__(self, enabled):
        self.enabled = enabled

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

