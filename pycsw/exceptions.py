"""Custom exception classes for pycsw"""

import logging

from pycsw.core.etree import etree
from pycsw.core import util


LOGGER = logging.getLogger(__name__)


class PycswError(Exception):
    """A base class for all pycsw exceptions"""

    def __init__(self, code, locator, text):
        self.code = code
        self.locator = locator
        self.text = text

    # FIXME - This functionality should be provided by the code that catches the error
    #def to_xml(self):
    #    language = self.pycsw_server.language
    #    ogc_schemas_base = self.pycsw_server.ogc_schemas_base
    #    ows_namespace = {
    #        util.CSW_VERSION_2_0_2: "ows",
    #        util.CSW_VERSION_3_0_0: "ows20",
    #    }.get(self.pycsw_server.csw_version)

    #    ns = self.pycsw_server.context.namespaces
    #    node = etree.Element(
    #        "{{{}}}ExceptionReport".format(ns[ows_namespace]),
    #        nsmap=ns,
    #        version=self.EXCEPTION_REPORT_VERSION,
    #        language=self.pycsw_server.language
    #    )
    #    node.set(
    #        "{{{}}}schemaLocation".format(ns["xsi"]),
    #        "{} {}/ows/2.0/owsExceptionReport.xsd".format(
    #            ns[ows_namespace],
    #            self.pycsw_server.ogc_schemas_base
    #        )
    #    )
    #    exception = etree.SubElement(
    #        node, "{{{}}}Exception".format(ns[ows_namespace]),
    #        exceptionCode=self.code, locator=self.locator
    #    )
    #    exception_text = etree.SubElement(
    #        exception, "{{{}}}ExceptionText".format(ns[ows_namespace]))
    #    exception_text.text = self.text
    #    return node

    def __str__(self):
        return ("{0.code} - {0.locator}: {0.text}".format(self))

