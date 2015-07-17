"""
Metadata parser classes for dealing with OGC web services
"""

import logging

from .. import util
from ..etree import etree
from ...plugins.profiles.apiso.apiso import APISO


LOGGER = logging.getLogger(__name__)


class OwsParser(object):
    """
    Base class for parsing metadata for OGC web services
    """

    def parse(self, url):
        pass

    def capabilities_to_iso(self, record, capabilities, context):
        """Creates ISO metadata from Capabilities XML"""

        apiso_obj = APISO(context.model, context.namespaces, context)
        apiso_obj.ogc_schemas_base = 'http://schemas.opengis.net'
        apiso_obj.url = context.url
        queryables = dict(apiso_obj.repository['queryables']['SupportedISOQueryables'].items() + apiso_obj.repository['queryables']['SupportedISOQueryables'].items())
        iso_xml = apiso_obj.write_record(record, 'full', 'http://www.isotc211.org/2005/gmd', queryables, capabilities)
        return etree.tostring(iso_xml)

    def _get_wkt_geometry(self, metadata_content):
        """Return the bounding box and crs of an input metadata content

        The returned bounding box is expressed as WellKnownText
        """

        wkt_geometry = None
        bbox, crs = metadata_content.boundingBox
        crs_code = crs.split(":")[1]
        if bbox is not None:
            wkt_geometry = util.bbox2wktpolygon(
                '{0[0]},{0[1]},{0[2]},{0[3]}'.format(bbox))
        return wkt_geometry, crs_code

