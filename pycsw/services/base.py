import logging

logger = logging.getLogger(__name__)


class Service:
    _name = ""
    _version = ""

    @property
    def identifier(self):
        return "{0._name}_v{0._version}".format(self)

    @classmethod
    def from_config(cls, **config_keys):
        instance = cls()
        return instance

