"""
ISO Application Profile for pycsw.
"""

from __future__ import absolute_import
import logging

from owslib.iso import MD_Metadata
from geolinks.links import sniff_link

from .base import BaseProfile
from ..core.configuration.properties import CswProperty
from ..core.models import Record
from ..core import util


LOGGER = logging.getLogger(__name__)


class IsoApplicationProfile(BaseProfile):
    """
    Notes on the ISO Application Profile:

    * No additional CSWT operations are defined
    * Apart from GetCapabilities, all operations must support SOAP v1.2
    * Responses are XML encoded
    * KVP **parameter names** are case insensitive
    * KVP **parameter values** are case sensitive
    """
    TYPENAME = "gmd:MD_Metadata"
    BRIEF_SET = "brief"
    SUMMARY_SET = "summary"
    FULL_SET = "full"

    def __init__(self):
        super(IsoApplicationProfile, self).__init__()
        self.name = "apiso"
        self.version = "1.0.0"
        self.typenames = [self.TYPENAME]
        self.elementsetnames = [self.BRIEF_SET, self.SUMMARY_SET,
                                self.FULL_SET]
        self.outputformats = {"xml": "application/xml"}
        self.outputschemas = {
            "csw": "http://www.opengis.net/cat/csw/2.0.2",
            "gmd": "http://www.isotc211.org/2005/gmd",
        }
        self.namespaces = self.namespaces.copy()
        self.namespaces.update({
            "gmd": "http://www.isotc211.org/2005/gmd",
            "apiso": "http://www.opengis.net/cat/csw/apiso/1.0",
            "gco": "http://www.isotc211.org/2005/gco",
            "srv": "http://www.isotc211.org/2005/srv",
            "xlink": "http://www.w3.org/1999/xlink"
        })
        #  use these when the INSPIRE extension is activated
        self.inspire_namespaces = {
            "inspire_ds": "http://inspire.ec.europa.eu/schemas/inspire_ds/1.0",
            "inspire_common": "http://inspire.ec.europa.eu/schemas/common/1.0"
        }
        self.core_iso_queryables = [
            CswProperty(
                "apiso:Subject", Record.keywords,
                x_path='gmd:identificationInfo/gmd:MD_Identification/'
                       'gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/'
                       'gco:CharacterString|gmd:identificationInfo/'
                       'gmd:MD_DataIdentification/gmd:topicCategory/'
                       'gmd:MD_TopicCategoryCode',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Title", Record.title,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:citation/gmd:CI_Citation/gmd:title/'
                       'gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Abstract", Record.abstract,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:abstract/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Format", Record.format,
                x_path='gmd:distributionInfo/gmd:MD_Distribution/'
                       'gmd:distributionFormat/gmd:MD_Format/gmd:name/'
                       'gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Identifier", Record.format,
                x_path='gmd:fileIdentifier/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Modified", Record.date_modified,
                x_path="gmd:dateStamp/gco:Date",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Type", Record.type,
                x_path="gmd:hierarchyLevel/gmd:MD_ScopeCode",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:BoundingBox", Record.wkt_geometry,
                x_path="apiso:BoundingBox",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:CRS", Record.crs,
                x_path='concat("urn:ogc:def:crs:","gmd:referenceSystemInfo/'
                       'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
                       'gmd:RS_Identifier/gmd:codeSpace/'
                       'gco:CharacterString",":","gmd:referenceSystemInfo/'
                       'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
                       'gmd:RS_Identifier/gmd:version/'
                       'gco:CharacterString",":","gmd:referenceSystemInfo/'
                       'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
                       'gmd:RS_Identifier/gmd:code/gco:CharacterString")',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:AlternateTitle", Record.title_alternate,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:citation/gmd:CI_Citation/gmd:alternateTitle/"
                       "gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:RevisionDate", Record.date_revision,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:citation/gmd:CI_Citation/gmd:date/'
                       'gmd:CI_Date[gmd:dateType/gmd:CI_DateTypeCode/@'
                       'codeListValue="revision"]/gmd:date/gco:Date',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:CreationDate", Record.date_creation,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:citation/gmd:CI_Citation/gmd:date/'
                       'gmd:CI_Date[gmd:dateType/gmd:CI_DateTypeCode/'
                       '@codeListValue="creation"]/gmd:date/gco:Date',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:PublicationDate", Record.date_publication,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:citation/gmd:CI_Citation/gmd:date/'
                       'gmd:CI_Date[gmd:dateType/gmd:CI_DateTypeCode/'
                       '@codeListValue="publication"]/gmd:date/gco:Date',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:OrganisationName", Record.organization,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
                       'gmd:organisationName/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:HasSecurityConstraints", Record.securityconstraints,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:resourceConstraints/gmd:MD_SecurityConstraints',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Language", Record.language,
                x_path='gmd:language/gmd:LanguageCode|gmd:language/'
                       'gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ParentIdentifier", Record.parentidentifier,
                x_path='gmd:parentIdentifier/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:KeywordType", Record.keywordtype,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/"
                       "gmd:MD_KeywordTypeCode",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:TopicCategory", Record.topicategory,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:topicCategory/gmd:MD_TopicCategoryCode",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ResourceLanguage", Record.resourcelanguage,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:code/"
                       "gmd:MD_LanguageTypeCode",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:GeographicDescriptionCode", Record.geodescode,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:extent/gmd:EX_Extent/gmd:geographicElement/"
                       "gmd:EX_GeographicDescription/gmd:geographicIdentifier/"
                       "gmd:MD_Identifier/gmd:code/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Denominator", Record.denominator,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:spatialResolution/gmd:MD_Resolution/"
                       "gmd:equivalentScale/gmd:MD_RepresentativeFraction/"
                       "gmd:denominator/gco:Integer",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:DistanceValue", Record.distancevalue,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/"
                       "gco:Distance",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:DistanceUOM", Record.distanceuom,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/"
                       "gco:Distance/@uom",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:TempExtent_begin", Record.time_begin,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:extent/gmd:EX_Extent/gmd:temporalElement/"
                       "gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/"
                       "gml:beginPosition",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:TempExtent_end", Record.time_end,
                x_path="gmd:identificationInfo/gmd:MD_DataIdentification/"
                       "gmd:extent/gmd:EX_Extent/gmd:temporalElement/"
                       "gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/"
                       "gml:endPosition",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:AnyText", Record.anytext,
                x_path="//",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ServiceType", Record.servicetype,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:serviceType/gco:LocalName",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ServiceTypeVersion", Record.servicetypeversion,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:serviceTypeVersion/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Operation", Record.operation,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:containsOperations/srv:SV_OperationMetadata/"
                       "srv:operationName/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:CouplingType", Record.couplingtype,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:couplingType/srv:SV_CouplingType",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:OperatesOn", Record.operateson,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:operatesOn/gmd:MD_DataIdentification/gmd:citation/"
                       "gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/"
                       "gmd:code/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:OperatesOnIdentifier", Record.operatesonidentifier,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:coupledResource/srv:SV_CoupledResource/"
                       "srv:identifier/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:OperatesOnName", Record.operatesoname,
                x_path="gmd:identificationInfo/srv:SV_ServiceIdentification/"
                       "srv:coupledResource/srv:SV_CoupledResource/"
                       "srv:operationName/gco:CharacterString",
                typenames=[self.TYPENAME],
            ),
        ]
        self.additional_queryables = [
            CswProperty(
                "apiso:Degree", Record.degree,
                x_path='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
                       'gmd:DQ_DomainConsistency/gmd:result/'
                       'gmd:DQ_ConformanceResult/gmd:pass/gco:Boolean',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:AccessConstraints", Record.accessconstraints,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
                       'gmd:accessConstraints/gmd:MD_RestrictionCode',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:OtherConstraints", Record.otherconstraints,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
                       'gmd:otherConstraints/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Classification", Record.classification,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
                       'gmd:accessConstraints/gmd:MD_ClassificationCode',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ConditionApplyingToAccessAndUse",
                Record.conditionapplyingtoaccessanduse,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:useLimitation/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Lineage", Record.lineage,
                x_path='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:lineage/'
                       'gmd:LI_Lineage/gmd:statement/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:ResponsiblePartyRole", Record.responsiblepartyrole,
                x_path='gmd:contact/gmd:CI_ResponsibleParty/gmd:role/'
                       'gmd:CI_RoleCode',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:SpecificationTitle", Record.specificationtitle,
                x_path='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
                       'gmd:DQ_DomainConsistency/gmd:result/'
                       'gmd:DQ_ConformanceResult/gmd:specification/'
                       'gmd:CI_Citation/gmd:title/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:SpecificationDate", Record.specificationdate,
                x_path='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
                       'gmd:DQ_DomainConsistency/gmd:result/'
                       'gmd:DQ_ConformanceResult/gmd:specification/'
                       'gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/'
                       'gco:Date',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:SpecificationDateType", Record.specificationdatetype,
                x_path='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
                       'gmd:DQ_DomainConsistency/gmd:result/'
                       'gmd:DQ_ConformanceResult/gmd:specification/'
                       'gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/'
                       'gmd:CI_DateTypeCode',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Creator", Record.creator,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
                       'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
                       '@codeListValue="originator"]/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Publisher", Record.publisher,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
                       'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
                       '@codeListValue="publisher"]/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Contributor", Record.contributor,
                x_path='gmd:identificationInfo/gmd:MD_DataIdentification/'
                       'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
                       'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
                       '@codeListValue="contributor"]/gco:CharacterString',
                typenames=[self.TYPENAME],
            ),
            CswProperty(
                "apiso:Relation", Record.relation,
                x_path='gmd:identificationInfo/gmd:MD_Data_Identification/'
                       'gmd:aggregationInfo',
                typenames=[self.TYPENAME],
            ),
        ]
        self.properties = self.core_iso_queryables + self.additional_queryables

    def deserialize_record(self, raw_record):
        exml = self._parse_to_element_tree(raw_record)
        md = MD_Metadata(exml)
        record = Record(
            identifier=md.identifier,
            typename=self.TYPENAME,
            schema=self.outputschemas["gmd"],
            mdsource="local",
            insert_date = util.get_today_and_now(),
            xml=md.xml,
            anytext=util.get_anytext(exml),
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

    def serialize_record(self, record, output_format=None, output_schema=None,
                         element_set_name=None, element_names=None):
        raise NotImplementedError
