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
    FULL_RECORD = "csw:Record"
    BRIEF_RECORD = "csw:BriefRecord"
    SUMMARY_RECORD = "csw:SummaryRecord"
    BRIEF_SET = "brief"
    SUMMARY_SET = "summary"
    FULL_SET = "full"

    # attributes that all profiles should implement
    name = "common"
    typenames = [FULL_RECORD, BRIEF_RECORD, SUMMARY_RECORD]
    elementsetnames = [BRIEF_SET, SUMMARY_SET, FULL_SET]
    outputformats = {
        "xml": "application/xml"
    }
    outputschemas = {
        "csw202": "http://www.opengis.net/cat/csw/2.0.2",
    }
    namespaces = {
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
        "ows": "http://www.opengis.net/ows",
    }

    # Properties of CSW core catalogue schema.
    # Refer to section 6.3.2 of the CSW standard for more details.
    # The order by which these properties are defined is important!
    # It is used when serializing to XML.
    # TODO: add the remaining, optional properties
    properties = [
        CswProperty("dc:identifier", Record.identifier,
                    typenames=[FULL_RECORD, SUMMARY_RECORD, BRIEF_RECORD],
                    elementsetnames=[BRIEF_SET, SUMMARY_SET, FULL_SET]),
        CswProperty("dc:title", Record.title,
                    typenames=[FULL_RECORD, SUMMARY_RECORD, BRIEF_RECORD],
                    elementsetnames=[BRIEF_SET, SUMMARY_SET, FULL_SET]),
        CswProperty("dc:type", Record.type,
                    typenames=[FULL_RECORD, SUMMARY_RECORD, BRIEF_RECORD],
                    elementsetnames=[BRIEF_SET, SUMMARY_SET, FULL_SET]),
        CswProperty("dc:subject", Record.keywords,
                    typenames=[FULL_RECORD, SUMMARY_RECORD],
                    elementsetnames=[SUMMARY_SET, FULL_SET]),
        CswProperty("dc:format", Record.format,
                    typenames=[FULL_RECORD, SUMMARY_RECORD],
                    elementsetnames=[SUMMARY_SET, FULL_SET]),
        CswProperty("dc:relation", Record.relation,
                    typenames=[FULL_RECORD, SUMMARY_RECORD],
                    elementsetnames=[SUMMARY_SET, FULL_SET]),
        CswProperty("dct:modified", Record.date_modified,
                    typenames=[FULL_RECORD, SUMMARY_RECORD],
                    elementsetnames=[SUMMARY_SET, FULL_SET]),
        CswProperty("dct:abstract", Record.abstract,
                    typenames=[FULL_RECORD, SUMMARY_RECORD],
                    elementsetnames=[SUMMARY_SET, FULL_SET]),
        CswProperty("dc:creator", Record.creator,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:publisher", Record.publisher,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:contributor", Record.contributor,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:source", Record.source,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:language", Record.language,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:rights", Record.accessconstraints,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dc:date", Record.date,
                    typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        # non queryables
        CswProperty("pycsw:AlternateTitle", Record.title_alternate,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:ParentIdentifier", Record.parentidentifier,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:TempExtent_begin", Record.time_begin,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:TempExtent_end", Record.time_end,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:ResourceLanguage", Record.resourcelanguage,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:OrganizationName", Record.organization,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:AccessConstraints", Record.accessconstraints,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:OtherConstraints", Record.otherconstraints,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:CreationDate", Record.date_creation,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:PublicationDate", Record.date_publication,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("pycsw:Modified", Record.date_modified,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        CswProperty("dct:references", Record.links,
                    is_queryable=False, typenames=[FULL_RECORD],
                    elementsetnames=[FULL_SET]),
        # additional core queryables
        CswProperty("ows:BoundingBox", Record.wkt_geometry,
                    typenames=[FULL_RECORD, SUMMARY_RECORD, BRIEF_RECORD],
                    elementsetnames=[BRIEF_SET, SUMMARY_SET, FULL_SET]),
        CswProperty("csw:AnyText", Record.anytext, is_returnable=False,
                    typenames=[FULL_RECORD]),
    ]

    def deserialize_record(self, raw_record):
        """Convert a raw metadata representation to pycsw's internal format.

        :param raw_record:
        :return:
        """

        if not isinstance(raw_record, etree._Element):
            try:
                # FIXME: harden this XML parsing or move it out of here
                exml = etree.parse(raw_record)
            except Exception:
                raise
        else:
            exml = raw_record
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

    def serialize_record(self, record, outputschema=None,
                         elementsetname=None, elementnames=None,
                         outputformat=None):
        """
        Render pycsw's representation of a record to the outputformat

        Apparently, element order is not relevant for the Full elementsetname
        however, it is important for Brief and Summary
        check the record.xsd file of OGC's CSW schema for more details

        :param record:
        :param outputschema:
        :param elementsetname:
        :param elementnames:
        :param outputformat:
        :return:
        """

        outputschema = outputschema or self.outputschemas["csw202"]
        outputformat = outputformat or self.outputformats["xml"]
        is_record = record.typename == self.FULL_RECORD
        is_full = elementsetname == self.FULL_SET
        is_csw202 = outputschema == self.outputschemas["csw202"]
        is_service = record.type == "service"
        if is_record and is_full and is_csw202 and not is_service:
            # record.xml is already the serialized record
            LOGGER.debug("No processing required, returning the raw record "
                         "xml, as is saved in the repository")
            exml = etree.parse(record.xml)
        else:
            if elementsetname is not None:
                # get the returnables and typename
                returnables = [p for p in self.properties if
                               p.is_returnable and
                               elementsetname in p.elementsetnames]
                typename = {
                    self.BRIEF_SET: self.BRIEF_RECORD,
                    self.SUMMARY_SET: self.SUMMARY_RECORD,
                    self.FULL_SET: self.FULL_RECORD
                }.get(elementsetname)
            elif elementnames is not None:
                returnables = [p for p in self.properties if
                               p.is_returnable and p.name in elementnames]
                typename = self.FULL_RECORD
            else:
                raise RuntimeError("Request is invalid. It does not feature "
                                   "elementsetname nor elementnames")
            schema_serializer = {
                self.outputschemas["csw202"]: self._serialize_with_csw202,
                # self.outputschemas["csw300"]: self._serialize_with_csw300,
            }.get(outputschema)
            exml = schema_serializer(record, returnables, typename)
        format_serializer = {
            self.outputformats["xml"]: self.serialize_to_xml,
        }.get(outputformat)
        result = format_serializer(exml)
        return result

    def _serialize_with_csw202(self, record, returnables, typename):
        exml = etree.Element(util.nspath_eval(typename, self.namespaces),
                             nsmap=self.namespaces)
        for returnable in returnables:
            if returnable.name == "ows:BoundingBox":
                try:
                    self._write_boundingbox(record, returnable, exml)
                except Exception as err:
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
