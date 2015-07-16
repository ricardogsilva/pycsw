import logging
from uuid import uuid1

from owslib.fgdc import Metadata

from ..models import Record
from ..configuration.configuration import Context
from .. import util


LOGGER = logging.getLogger(__name__)


class FgdcParser(object):

    def parse(self, xml_record):
        md = Metadata(xml_record)
        identifier = md.idinfo.datasetid or uuid1().get_urn()
        record = Record(
            identifier=identifier,
            typename="fgdc:metadata",
            schema=Context.namespaces["fgdc"],
            mdsource='local',
            insert_date=util.get_today_and_now(),
            xml=md.xml,
            anytext=util.get_anytext(xml_record),
            language="en-US",
            accessconstraints=md.idinfo.accconst,
            otherconstraints=md.idinfo.useconst,
            date=md.metainfo.metd,
        )
        try:
            record.abstract = md.idinfo.descript.abstract
        except AttributeError:
            pass
        try:
            if md.idinfo.keywords.theme:
                record.keywords = ','.join(
                    md.idinfo.keywords.theme[0]['themekey'])
        except AttributeError:
            pass
        try:
            record.time_begin = md.idinfo.timeperd.timeinfo.rngdates.begdate
            record.time_end = md.idinfo.timeperd.timeinfo.rngdates.enddate
        except AttributeError:
            pass
        try:
            record.creator = md.idinfo.origin
            record.publisher = md.idinfo.origin
            record.contributor = md.idinfo.origin
        except AttributeError:
            pass
        try:
            record.organization = md.idinfo.ptcontac.cntorg
        except AttributeError:
            pass
        try:
            record.type = md.idinfo.citation.citeinfo['geoform']
            record.title = md.idinfo.citation.citeinfo['title']
            record.date_publication = md.idinfo.citation.citeinfo['pubdate']
            record.format = md.idinfo.citation.citeinfo['geoform']
        except AttributeError:
            pass
        links = self.collect_links(md)
        if len(links) > 0:
            record.links = '^'.join(links)

        try:
            bbox = md.idinfo.spdom.bbox
            record.wkt_geometry = util.bbox2wktpolygon(
                "{0.minx},{0.miny},{0.maxx},{0.maxy}".format(bbox))
        except (AttributeError, Exception):
            pass
        return record

    @staticmethod
    def collect_links(metadata):
        links = []
        if metadata.idinfo.citation.citeinfo['onlink']:
            for link in metadata.idinfo.citation.citeinfo['onlink']:
                tmp = ',,,{}'.format(link)
                links.append(tmp)
        try:
            for link in metadata.distinfo.stdorder["digform"]:
                links.append(',{0[name]},,{0[url]}'.format(link))
        except AttributeError:
            pass
        return links
