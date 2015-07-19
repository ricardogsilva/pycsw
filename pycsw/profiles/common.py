"""
Common Element Set for pycsw.

It is implemented as a core profile.
"""

import logging

from owslib.csw import CswRecord

from ..core import util
from ..core.models import Record
from ..core.configuration import queryables
from ..core.etree import etree
from .profile import Profile


LOGGER = logging.getLogger(__name__)

class CommonElementSet(Profile):
    RECORD = "csw:Record"
    BRIEF_RECORD = "csw:BriefRecord"
    SUMMARY_RECORD = "csw:SummaryRecord"
    BRIEF_SET = "brief"
    SUMMARY_SET = "summary"
    FULL_SET = "full"

    name = "common"
    typenames = [RECORD, BRIEF_RECORD, SUMMARY_RECORD]
    outputschemas = {
        "csw202": "http://www.opengis.net/cat/csw/2.0.2",
    }
    outputformats = {
        "xml": "application/xml"
    }
    elementsetnames = [BRIEF_SET, SUMMARY_SET, FULL_SET]
    namespaces = {
       "csw": "http://www.opengis.net/cat/csw/2.0.2",
    }

    def add_properties(self):
        self.add_property(queryables.dc_identifier)
        self.add_property(queryables.dc_title)
        self.add_property(queryables.dc_type)
        self.add_property(queryables.ows_BoundingBox)
        self.add_property(queryables.dc_subject,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dc_format,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dc_relation,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dct_modified,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dct_abstract,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dct_references,
                          elementsetnames=["summary", "full"])
        self.add_property(queryables.dc_creator, elementsetnames=["full"])
        self.add_property(queryables.dc_publisher, elementsetnames=["full"])
        self.add_property(queryables.dc_contributor, elementsetnames=["full"])
        self.add_property(queryables.dc_source, elementsetnames=["full"])
        self.add_property(queryables.dc_language, elementsetnames=["full"])
        self.add_property(queryables.dc_rights, elementsetnames=["full"])
        self.add_property(queryables.csw_AnyText, returnable=False)

    def deserialize_record(self, raw_record):
        exml = etree.parse(raw_record)
        md = CswRecord(exml)
        record = Record(
            identifier=md.identifier,
            typename="csw:Record",
            schema=self.namespaces["csw"],
            mdsource='local',
            insert_date=util.get_today_and_now(),
            xml=md.xml,
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
        is_record = record.typename == self.RECORD
        is_full = elementsetname == self.FULL_SET
        is_csw202 = outputschema == self.outputschemas["csw202"]
        is_service = record.type == "service"
        if is_record and is_full and is_csw202 and not is_service:
            # record.xml is already the serialized record
            result = etree.parse(record.xml)
        else:
            returnables_getter = {
                self.BRIEF_SET: self._get_brief_returnables,
                self.SUMMARY_SET: self._get_summary_returnables,
                self.FULL_SET: self._get_full_returnables,
            }.get(elementsetname)
            if returnables_getter:
                returnables, typename = returnables_getter()
            else:
                returnables, typename = self._get_custom_returnables(
                    elementnames)
            schema_serializer = {
                self.outputschemas["csw202"]: self._serialize_with_csw202_schema,
            }.get(outputschema)
            exml = schema_serializer(record, returnables, typename)
            format_serializer = {
                self.outputformats["xml"]: self.serialize_to_xml,
            }.get(outputformat)
            result = format_serializer(exml)
        return result

    def _get_brief_returnables(self):
        result = [
            self.mandatory_queryables["dc:identifier"],
            self.mandatory_queryables["dc:title"],
            self.mandatory_queryables["dc:type"],
        ]
        typename = self.BRIEF_RECORD
        return result, typename

    def _get_summary_returnables(self):
        result = []
        typename = self.SUMMARY_RECORD
        for queryable in self.mandatory_queryables
        return result, typename

    def _get_full_returnables(self):
        result = self.mandatory_returnables.copy()
        result.update(self.additional_returnables)
        typename = self.RECORD
        return result, typename

    def _get_custom_returnables(self, names):
        result = dict()
        typename = self.RECORD
        all_returnables = self.mandatory_returnables.copy()
        all_returnables.update(self.additional_returnables)
        for name in names:
            result[name] = all_returnables[name]
        return result, typename

    def _serialize_with_csw202_schema(self, record, returnables, typename):
        exml = etree.Element(util.nspath_eval(typename, self.namespaces))
        identifier = etree.SubElement(
            record, util.nspath_eval("dc:identifier", self.namespaces))
        identifier.text = record.identifier

        for r in returnables:
            element = etree.SubElement(
                record, util.nspath_eval(r.name, self.namespaces))
            element.text = getattr(record, r.map_to)





            etree.SubElement(record,
                             util.nspath_eval('dc:identifier', self.parent.context.namespaces)).text = \
                util.getqattr(recobj,
                              self.parent.context.md_core_model['mappings']['pycsw:Identifier'])

            for i in ['dc:title', 'dc:type']:
                val = util.getqattr(recobj, queryables[i]['dbcol'])
                if not val:
                    val = ''
                etree.SubElement(record, util.nspath_eval(i,
                                                          self.parent.context.namespaces)).text = val

            if self.parent.kvp['elementsetname'] in ['summary', 'full']:
                # add summary elements
                keywords = util.getqattr(recobj, queryables['dc:subject']['dbcol'])
                if keywords is not None:
                    for keyword in keywords.split(','):
                        etree.SubElement(record,
                                         util.nspath_eval('dc:subject',
                                                          self.parent.context.namespaces)).text = keyword

                val = util.getqattr(recobj, queryables['dc:format']['dbcol'])
                if val:
                    etree.SubElement(record,
                                     util.nspath_eval('dc:format',
                                                      self.parent.context.namespaces)).text = val

                # links
                rlinks = util.getqattr(recobj,
                                       self.parent.context.md_core_model['mappings']['pycsw:Links'])

                if rlinks:
                    links = rlinks.split('^')
                    for link in links:
                        linkset = link.split(',')
                        etree.SubElement(record,
                                         util.nspath_eval('dct:references',
                                                          self.parent.context.namespaces),
                                         scheme=linkset[2]).text = linkset[-1]

                for i in ['dc:relation', 'dct:modified', 'dct:abstract']:
                    val = util.getqattr(recobj, queryables[i]['dbcol'])
                    if val is not None:
                        etree.SubElement(record,
                                         util.nspath_eval(i, self.parent.context.namespaces)).text = val

            if self.parent.kvp['elementsetname'] == 'full':  # add full elements
                for i in ['dc:date', 'dc:creator', \
                          'dc:publisher', 'dc:contributor', 'dc:source', \
                          'dc:language', 'dc:rights']:
                    val = util.getqattr(recobj, queryables[i]['dbcol'])
                    if val:
                        etree.SubElement(record,
                                         util.nspath_eval(i, self.parent.context.namespaces)).text = val

            # always write out ows:BoundingBox
            bboxel = write_boundingbox(getattr(recobj,
                                               self.parent.context.md_core_model['mappings']['pycsw:BoundingBox']),
                                       self.parent.context.namespaces)

            if bboxel is not None:
                record.append(bboxel)
        return record

    def serialize_to_xml(self, exml):
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
