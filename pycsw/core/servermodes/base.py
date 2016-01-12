"""Base class for pycsw operational modes."""

import logging

LOGGER = logging.getLogger(__name__)


class ModeBase(object):

    def __init__(self, pycsw_server=None):
        # at the moment the pycsw_server reference is needed in order to
        # have the context accessible. In the future this could probably
        # become unnecessary.
        self.server = pycsw_server

    def dispatch_kvp(self, kvp_params):
        raise NotImplementedError

    def dispatch_xml(self, xml_element):
        raise NotImplementedError

    def dispatch_json(self, json_element):
        raise NotImplementedError
