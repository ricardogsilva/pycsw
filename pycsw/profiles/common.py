"""
Common Element Set for pycsw.

It is implemented as a core profile.
"""

from __future__ import absolute_import
import sys
import logging
from traceback import format_exception_only

from owslib.csw import CswRecord

from ..core import util
from ..core.models import Record
from ..core.configuration.properties import CswProperty
from ..core.etree import etree
from .base import BaseProfile


LOGGER = logging.getLogger(__name__)


class CommonElementSet(BaseProfile):
    """

    Properties of CSW core catalogue schema:

    * Refer to sections 6.3.2 and 10.2.5.3 of the CSW standard for more
      details.

    * The order by which the properties are defined is important!
      It is used when serializing to XML.

    * core queryables (OGC name): Subject, Title, Abstract, AnyText, Format,
                                  Identifier, Modified, Type, BoundingBox,
                                  CRS(!), Association

    * CRS queryable: Table 1 - 'Common queryable elements' of section 6.3.2
      states that if not specified, the CRS shall be a geographic
      CRS with the Greenwich prime meridian. We use WGS84.

    * AnyText queryable is not returnable

    * Identifier and Title are mandatory returnables. The other elements
      are optional

    * mapping of core queryables in the HTTP protocol:
      (OGC name - XML element name - substitute term)

      * Title       - dc:title        - dct:alternative
      *             - dc:creator      -
      * Subject     - dc:subject      -
      * Abstract    - dct:abstract    - dc:description
      *             - dc:publisher    -
      *             - dc:contributor  -
      * Modified    - dct:modified     - dc:date
      * Type        - dc:type         -
      * Format      - dc:format       - dct:extent
      * Identifier  - dc:identifier   - dct:bibliographicCitation
      * Source      - dc:source       -
      *             - dc:language     -
      * Association - dc:relation     - dct:conformsTo
      * BoundingBox - ows:BoundingBox -
      *             - dc:rights       - dct:license

    * other dc elements:

      * dc:coverage  - dct:spatial
    """

    FULL_RECORD = "csw:Record"
    BRIEF_RECORD = "csw:BriefRecord"
    SUMMARY_RECORD = "csw:SummaryRecord"
    BRIEF_SET = "brief"
    SUMMARY_SET = "summary"
    FULL_SET = "full"

    def __init__(self):
        super(CommonElementSet, self).__init__()
        self.name = "common"
        self.version = "2.0.2"
        self.typenames = [self.FULL_RECORD, self.BRIEF_RECORD,
                          self.SUMMARY_RECORD]
        self.elementsetnames = [self.BRIEF_SET, self.SUMMARY_SET,
                                self.FULL_SET]
        self.outputformats = {"xml": "application/xml"}
        self.outputschemas = {"csw": "http://www.opengis.net/cat/csw/2.0.2"}
        self.namespaces = self.namespaces.copy()
        self.namespaces.update({
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "ows": "http://www.opengis.net/ows",
        })
        self.properties = [
            CswProperty("dc:identifier", Record.identifier,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD,
                                   self.BRIEF_RECORD],
                        elementsetnames=[self.BRIEF_SET, self.SUMMARY_SET,
                                         self.FULL_SET]),
            CswProperty("dc:title", Record.title,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD,
                                   self.BRIEF_RECORD],
                        elementsetnames=[self.BRIEF_SET, self.SUMMARY_SET,
                                         self.FULL_SET]),
            CswProperty("dc:type", Record.type,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD,
                                   self.BRIEF_RECORD],
                        elementsetnames=[self.BRIEF_SET, self.SUMMARY_SET,
                                         self.FULL_SET]),
            CswProperty("dc:subject", Record.keywords,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD],
                        elementsetnames=[self.SUMMARY_SET, self.FULL_SET]),
            CswProperty("dc:format", Record.format,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD],
                        elementsetnames=[self.SUMMARY_SET, self.FULL_SET]),
            CswProperty("dc:relation", Record.relation,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD],
                        elementsetnames=[self.SUMMARY_SET, self.FULL_SET]),
            CswProperty("dct:modified", Record.date_modified,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD],
                        elementsetnames=[self.SUMMARY_SET, self.FULL_SET]),
            CswProperty("dct:abstract", Record.abstract,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD],
                        elementsetnames=[self.SUMMARY_SET, self.FULL_SET]),
            CswProperty("dc:creator", Record.creator,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dc:publisher", Record.publisher,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dc:contributor", Record.contributor,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dc:source", Record.source,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dc:language", Record.language,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dc:rights", Record.accessconstraints,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            # additional queryables
            CswProperty("dc:date", Record.date,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:alternative", Record.title_alternate,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:references", Record.links,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:isPartOf", Record.parentidentifier,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:temporal", Record.time_begin,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:temporal", Record.time_end,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:rightsHolder", Record.organization,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:accessRights", Record.accessconstraints,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:license", Record.otherconstraints,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:created", Record.date_creation,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            CswProperty("dct:issued", Record.date_publication,
                        typenames=[self.FULL_RECORD],
                        elementsetnames=[self.FULL_SET]),
            # final core queryables, that show up last
            CswProperty("ows:BoundingBox", Record.wkt_geometry,
                        typenames=[self.FULL_RECORD, self.SUMMARY_RECORD,
                                   self.BRIEF_RECORD],
                        elementsetnames=[self.BRIEF_SET, self.SUMMARY_SET,
                                         self.FULL_SET]),
            CswProperty("csw:AnyText", Record.anytext, is_returnable=False,
                        typenames=[self.FULL_RECORD]),
        ]

    def deserialize_record(self, raw_record):
        """Convert a raw metadata representation to pycsw's internal format.

        :param raw_record:
        :return:
        """

        exml = self._parse_to_element_tree(raw_record)
        md = CswRecord(exml)
        record = Record(
            # fields absolutely required for pycsw to work
            identifier=md.identifier,
            typename="csw:Record",
            schema=self.namespaces["csw"],
            mdsource='local',
            insert_date=util.get_today_and_now(),
            xml=md.xml,
            # properties of this profile
            anytext=util.get_anytext(exml),
            language=md.language,
            type=md.type,
            title=md.title,
            title_alternate=md.alternative,
            abstract=md.abstract,
            parentidentifier=md.ispartof,
            relation=md.relation,
            time_begin=md.temporal,
            time_end=md.temporal,
            resourcelanguage=md.language,
            creator=md.creator,
            publisher=md.publisher,
            contributor=md.contributor,
            organization=md.rightsholder,
            accessconstraints=md.accessrights,
            otherconstraints=md.license,
            date=md.date,
            date_creation=md.created,
            date_publication=md.issued,
            date_modified=md.modified,
            format=md.format,
            source=md.source,
        )
        if len(md.subjects) > 0 and None not in md.subjects:
            record.keywords = ",".join(md.subjects)
        links = self.collect_links(md)
        if len(links) > 0:
            record.links = '^'.join(links)
        if md.bbox is not None:
            try:
                tmp = '{0.minx},{0.miny},{0.maxx},{0.maxy}'.format(md.bbox)
                record.wkt_geometry = util.bbox2wktpolygon(tmp)
            except Exception:
                pass  # coordinates are corrupted
        return record

    def serialize_record(self, record, output_format=None, output_schema=None,
                         element_set_name=None, element_names=None):
        """
        Render pycsw's representation of a record to the outputformat

        Apparently, element order is not relevant for the Full elementsetname
        however, it is important for Brief and Summary
        check the record.xsd file of OGC's CSW schema for more details

        :param record:
        :param output_format:
        :param output_schema:
        :param element_set_name:
        :param element_names:
        :return:
        """

        output_schema = output_schema or self.outputschemas["csw"]
        output_format = output_format or self.outputformats["xml"]
        is_record = record.typename == self.FULL_RECORD
        is_full = element_set_name == self.FULL_SET
        is_service = record.type == "service"
        if is_record and is_full and not is_service:
            # record.xml is already the serialized record
            LOGGER.debug("No processing required, returning the raw record "
                         "xml, as is saved in the repository")
            exml = etree.fromstring(record.xml)
        else:
            if element_set_name is not None:
                # get the returnables and typename
                returnables = [p for p in self.properties if
                               p.is_returnable and
                               element_set_name in p.elementsetnames]
                typename = {
                    self.BRIEF_SET: self.BRIEF_RECORD,
                    self.SUMMARY_SET: self.SUMMARY_RECORD,
                    self.FULL_SET: self.FULL_RECORD
                }.get(element_set_name)
            elif element_names is not None:
                returnables = [p for p in self.properties if
                               p.is_returnable and p.name in element_names]
                typename = self.FULL_RECORD
            else:
                raise RuntimeError("Request is invalid. It does not feature "
                                   "elementsetname nor elementnames")
            exml = self._serialize_to_csw_record(record, returnables, typename)
        format_serializer = {
            self.outputformats["xml"]: self.serialize_to_xml,
        }.get(output_format)
        result = format_serializer(exml)
        return result

    def _serialize_to_csw_record(self, record, returnables, typename):
        exml = etree.Element(util.nspath_eval(typename, self.namespaces),
                             nsmap=self.namespaces)
        for returnable in returnables:
            if returnable.name == "ows:BoundingBox":
                try:
                    self._write_boundingbox(record, returnable, exml)
                except Exception:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    msg = "".join(format_exception_only(exc_type, exc_value))
                    LOGGER.warning(msg)
            elif returnable.name == "dc:subject":
                for keyword in record.keywords.split(","):
                    subject_element = etree.SubElement(
                        exml, util.nspath_eval("dc:subject", self.namespaces))
                    subject_element.text = keyword
            elif returnable.name == "dct:references":
                for link in record.links.split("^"):
                    linkset = link.split(",")
                    references_element = etree.SubElement(
                        exml,
                        util.nspath_eval('dct:references', self.namespaces),
                        scheme=linkset[2])
                    references_element.text = linkset[-1]
            else:  # process the element normally
                value = returnable.get_value(record)
                if value is not None:
                    element = etree.SubElement(exml, util.nspath_eval(
                        returnable.name, self.namespaces))
                    element.text = value
        return exml

    def _write_boundingbox(self, record, returnable, exml_parent):
        """Generate ows:BoundingBox"""

        if record.wkt_geometry is not None:
            bbox = util.wkt2geom(record.wkt_geometry)
            if len(bbox) == 4:
                bbox_element = etree.SubElement(
                    exml_parent,
                    util.nspath_eval(returnable.name, self.namespaces)
                )
                lower_corner_element = etree.SubElement(
                    bbox_element,
                    util.nspath_eval("ows:LowerCorner", self.namespaces),
                    crs="urn:x-ogc:def:crs:EPSG:6.11:4326",
                    dimensions="2"
                )
                lower_corner_element.text = "{0[1]} {0[0]}".format(bbox)
                upper_corner_element = etree.SubElement(
                    bbox_element,
                    util.nspath_eval("ows:UpperCorner", self.namespaces),
                    crs="urn:x-ogc:def:crs:EPSG:6.11:4326",
                    dimensions="2"
                )
                upper_corner_element.text = "{0[3]} {0[2]}".format(bbox)

    @staticmethod
    def serialize_to_xml(exml):
        return etree.tostring(exml, encoding="utf8")

    @staticmethod
    def collect_links(metadata):
        links = []
        for ref in metadata.references:
            links.append(',,{0[scheme]},{0[url]}'.format(ref))
        for uri in metadata.uris:
            links.append("{0[name]},{0[description]},{0[protocol]},"
                         "{0[url]}".format(uri))
        return links
