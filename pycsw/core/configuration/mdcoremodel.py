import json
import logging

from ..models import Record


LOGGER = logging.getLogger(__name__)


class MdCoreModel(object):
    typename = ""
    outputschema = ""
    _mappings = dict()

    @property
    def mappings(self):
        return self._mappings

    @mappings.setter
    def mappings(self, new_mappings):
        self._mappings.update(new_mappings)
        Record.remap_columns(self.mappings)

    def __init__(self, typename, outputschema, mappings_path=None):
        self.typename = typename
        self.outputschema = outputschema
        if mappings_path is not None:
            self.read_mappings(mappings_path)

    def read_mappings(self, mappings_path):
        try:
            with open(mappings_path) as fh:
                self.mappings = json.load(fh)
        except (IOError, ValueError) as err:
            raise RuntimeError("Invalid mappings_path: {}".format(err))
