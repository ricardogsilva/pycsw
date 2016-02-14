"""CSW operational mode for pycsw"""

import logging

from ... import exceptions
from .. import util
from .. import etree
from . import base

LOGGER = logging.getLogger(__name__)


class CswMode(base.ModeBase):

    accept_versions = {
        util.CSW_VERSION_2_0_2: "pycsw.ogc.csw.csw2.Csw202",
        util.CSW_VERSION_3_0_0: "pycsw.ogc.csw.csw3.Csw300"
    }
    # defaulting to 2.0.2 while 3.0.0 is not out
    default_version = util.CSW_VERSION_2_0_2

    def dispatch(self):
        raise NotImplementedError

    def dispatch_kvp(self, kvp_params):
        """Dispatch the input KVP request for processing."""
        self.validate_service(kvp_params.get("service"))
        try:
            operation = kvp_params["request"]
        except KeyError:
            raise exceptions.PycswError(exceptions.NO_APPLICABLE_CODE)
        if operation == util.CSW_OPERATION_GET_CAPABILITIES:
            versions = kvp_params.get("acceptversions",
                                      self.default_version).split(",")
            version = self.negotiate_version(versions)
        else:
            try:
                version = kvp_params["version"]
            except KeyError:
                raise exceptions.PycswError(
                    code=exceptions.MISSING_PARAMETER_VALUE,
                    locator="version"
                )
            else:
                self.validate_version(version)
        LOGGER.info("Accepted version {}".format(version))
        csw_interface = self.get_csw_interface(version)
        return csw_interface.dispatch_kvp(kvp_params)

    def dispatch_xml(self, xml_element):
        """Dispatch the input XML request for processing."""
        self.validate_service(xml_element.get("service"))
        qname = etree.etree.QName(xml_element)
        operation = qname.localname
        if operation == util.CSW_OPERATION_GET_CAPABILITIES:
            versions = xml_element.xpath(
                "./ows:AcceptVersions/ows:Version/text()",
                namespaces=self.server.context.namespaces
            )
            versions = versions or [self.default_version]
            version = self.negotiate_version(versions)
        else:
            try:
                version = xml_element.attrib["version"]
            except KeyError:
                raise exceptions.PycswError(
                    code=exceptions.MISSING_PARAMETER_VALUE,
                    locator="version"
                )
            else:
                self.validate_version(version)
        LOGGER.info("Accepted version {}".format(version))
        csw_interface = self.get_csw_interface(version)
        return csw_interface.dispatch_xml(xml_element)

    def get_csw_interface(self, version):
        csw_version_class_path = self.accept_versions[version]
        module, sep, type_ = csw_version_class_path.rpartition(".")
        csw_version_class = util.lazy_import_dependency(module, type_)
        return csw_version_class()

    def validate_version(self, version):
        if version not in self.accept_versions:
            raise exceptions.PycswError(
                code=exceptions.INVALID_PARAMETER_VALUE,
                locator="version"
            )

    def validate_service(self, service):
        if service != util.CSW_SERVICE:
            raise exceptions.PycswError(exceptions.NO_APPLICABLE_CODE)

    def negotiate_version(self, requested_versions):
        """Negotiate the version to retrieve for GetCapabilities requests."""
        for requested in requested_versions:
            if requested in self.accept_versions:
                valid_version = requested
                break
        else:  # none of the requested versions is acceptable
            raise exceptions.PycswError(exceptions.VERSION_NEGOTIATION_FAILED)
        return valid_version
