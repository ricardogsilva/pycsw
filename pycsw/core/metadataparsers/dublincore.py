import logging

from owslib.csw import CswRecord

from ..models import Record
from ..configuration.configuration import Context
from .. import util


LOGGER = logging.getLogger(__name__)


class DcParser(object):

    def parse(self, xml_record):
        md = CswRecord(xml_record)
        record = Record(
            identifier=md.identifier,
            typename="csw:Record",
            schema=Context.namespaces["csw"],
            mdsource='local',
            insert_date=util.get_today_and_now(),
            xml=md.xml,
            anytext=util.get_anytext(xml_record),
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

    @staticmethod
    def collect_links(metadata):
        links = []
        for ref in metadata.references:
            links.append(',,{0[scheme]},{0[url]}'.format(ref))
        for uri in metadata.uris:
            links.append("{0[name]},{0[description]},{0[protocol]},"
                         "{0[url]}".format(uri))
        return links
