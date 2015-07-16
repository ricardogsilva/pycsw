import logging

from geolinks.links import sniff_link
from owslib.iso import MD_Metadata

from ..models import Record
from .. import util
from ..configuration.configuration import Context

LOGGER = logging.getLogger(__name__)


class IsoParser(object):
    """
    Parses an elementtree record that conforms to the ISO19139 schema
    """

    def parse(self, xml_record):
        md = MD_Metadata(xml_record)
        record = Record(
            identifier=md.identifier,
            typename="gmd:MD_Metadata",
            schema=Context.namespaces['gmd'],
            mdsource='local',
            insert_date = util.get_today_and_now(),
            xml=md.xml,
            anytext=util.get_anytext(xml_record),
            language=md.language,
            type=md.hierarchy,
            parentidentifier=md.parentidentifier,
            date=md.datestamp,
            date_modified=md.datestamp,
            source=md.dataseturi
        )
        if md.referencesystem is not None:
            record.crs = 'urn:ogc:def:crs:EPSG:6.11:{}'.format(
                md.referencesystem.code)
        if hasattr(md, 'identification'):
            ident = md.identification
            record.title = ident.title
            record.title_alternate = ident.alternatetitle
            record.abstract = ident.abstract
            record.relation = ident.aggregationinfo
            if hasattr(ident, 'temporalextent_start'):
                record.time_begin = ident.temporalextent_start
            if hasattr(ident, 'temporalextent_end'):
                record.time_end = ident.temporalextent_end
            if len(ident.topiccategory) > 0:
                record.topicategory = ident.topiccategory[0]
            if len(ident.resourcelanguage) > 0:
                record.resourcelanguage = ident.resourcelanguage[0]
            if hasattr(ident, 'bbox'):
                try:
                    wkt = util.bbox2wktpolygon('{0.minx},{0.miny},{0.maxx},'
                                               '{0.maxy}'.format(ident.bbox))
                    record.wkt_geometry = wkt
                except Exception as err:  # coordinates are corrupted
                    LOGGER.warning(err)
            if (hasattr(ident, 'keywords') and len(ident.keywords) > 0):
                all_keywords = [item for sublist in ident.keywords for item in sublist['keywords'] if item is not None]
                record.keywords = ','.join(all_keywords)
                record.keywordtype = ident.keywords[0]['type']
            if (hasattr(ident, 'creator') and len(ident.creator) > 0):
                all_orgs = set([item.organization for item in ident.creator if hasattr(item, 'organization') and item.organization is not None])
                record.creator = ';'.join(all_orgs)
            if (hasattr(ident, 'publisher') and len(ident.publisher) > 0):
                all_orgs = set([item.organization for item in ident.publisher if hasattr(item, 'organization') and item.organization is not None])
                record.publisher = ';'.join(all_orgs)
            if (hasattr(ident, 'contributor') and len(ident.contributor) > 0):
                all_orgs = set([item.organization for item in ident.contributor if hasattr(item, 'organization') and item.organization is not None])
                record.contributor = ';'.join(all_orgs)
            if (hasattr(ident, 'contact') and len(ident.contact) > 0):
                all_orgs = set([item.organization for item in ident.contact if hasattr(item, 'organization') and item.organization is not None])
                record.organization = ';'.join(all_orgs)
            if len(ident.securityconstraints) > 0:
                record.securityconstraints = ident.securityconstraints[0]
            if len(ident.accessconstraints) > 0:
                record.accessconstraints = ident.accessconstraints[0]
            if len(ident.otherconstraints) > 0:
                record.otherconstraints = ident.otherconstraints[0]
            if hasattr(ident, 'date'):
                # TODO - Check data types of dates
                for datenode in ident.date:
                    if datenode.type == 'revision':
                        record.date_revision = datenode.date
                    elif datenode.type == 'creation':
                        record.date_creation = datenode.date
                    elif datenode.type == 'publication':
                        record.date_publication = datenode.date
            if hasattr(ident, 'extent') and hasattr(ident.extent, 'description_code'):
                record.geodescode = ident.extent.description_code
            if len(ident.denominators) > 0:
                record.denominator = ident.denominators[0]
            if len(ident.distance) > 0:
                record.distancevalue = ident.distance[0]
            if len(ident.uom) > 0:
                record.distanceuom = ident.uom[0]
            if len(ident.classification) > 0:
                record.classification = ident.classification[0]
            if len(ident.uselimitation) > 0:
                record.conditionapplyingtoaccessanduse = ident.uselimitation[0]
            # the next blocks seem fishy
            if hasattr(ident, 'format'):
                record.format = md.distribution.format
            if hasattr(ident, 'dataquality'):
                record.degree = md.dataquality.conformancedegree
                record.lineage = md.dataquality.lineage
                record.specificationtitle = md.dataquality.specificationtitle
                if hasattr(md.dataquality, 'specificationdate'):
                    record.specificationdate = \
                        md.dataquality.specificationdate[0].date
                    record.specificationdatetype = \
                        md.dataquality.specificationdate[0].datetype
        if md.serviceidentification is not None:
            record.servicetype = md.serviceidentification.type
            record.servicetypeversion = md.serviceidentification.version
            record.couplingtype = md.serviceidentification.couplingtype
        if hasattr(md, 'contact') and len(md.contact) > 0:
            record.responsiblepartyrole = md.contact[0].role
        links = []
        LOGGER.info('Scanning for links')
        if hasattr(md, 'distribution'):
            dist_links = []
            if hasattr(md.distribution, 'online'):
                LOGGER.debug('Scanning for gmd:transferOptions element(s)')
                dist_links.extend(md.distribution.online)
            if hasattr(md.distribution, 'distributor'):
                LOGGER.debug('Scanning for gmd:distributorTransferOptions element(s)')
                for dist_member in md.distribution.distributor:
                    dist_links.extend(dist_member.online)
            for link in dist_links:
                if link.url is not None and link.protocol is None:  # take a best guess
                    link.protocol = sniff_link(link.url)
                linkstr = ('{0.name},{0.description},{0.protocol},'
                           '{0.url}'.format(link))
                links.append(linkstr)
        try:
            LOGGER.debug('Scanning for srv:SV_ServiceIdentification links')
            for sident in md.identificationinfo:
                if hasattr(sident, 'operations'):
                    for sops in sident.operations:
                        for scpt in sops['connectpoint']:
                            LOGGER.debug('adding srv link %s', scpt.url)
                            linkstr = ('{0.name},{0.description},'
                                       '{0.protocol},{0.url}'.format(scpt))
                            links.append(linkstr)
        except Exception as err:  # srv: identification does not exist
            LOGGER.debug('no srv:SV_ServiceIdentification links found')
        if len(links) > 0:
            record.links = '^'.join(links)
        return record
