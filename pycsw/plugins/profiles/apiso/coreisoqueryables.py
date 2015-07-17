"""
Core ISO queryables for the apiso profile
"""

from ....core.configuration.queryables import CswQueryable
from ....core.models import Record

queryables = [
    CswQueryable(
        "apiso:Subject", Record.keywords,
        xpath='gmd:identificationInfo/gmd:MD_Identification/'
              'gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:keyword/'
              'gco:CharacterString|gmd:identificationInfo/'
              'gmd:MD_DataIdentification/gmd:topicCategory/'
              'gmd:MD_TopicCategoryCode'
    ),
    CswQueryable(
        "apiso:Title", Record.title,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/'
              'gmd:CI_Citation/gmd:title/gco:CharacterString'
    ),
    CswQueryable(
        "apiso:Abstract", Record.abstract,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/'
              'gco:CharacterString'
    ),
    CswQueryable(
        "apiso:Format", Record.format,
        xpath='gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat/'
              'gmd:MD_Format/gmd:name/gco:CharacterString'
    ),
    CswQueryable(
        "apiso:Identifier", Record.format,
        xpath='gmd:fileIdentifier/gco:CharacterString'
    ),
    CswQueryable(
        "apiso:Modified", Record.date_modified,
        xpath="gmd:dateStamp/gco:Date",
    ),
    CswQueryable(
        "apiso:Type", Record.type,
        xpath="gmd:hierarchyLevel/gmd:MD_ScopeCode",
    ),
    CswQueryable(
        "apiso:BoundingBox", Record.wkt_geometry,
        xpath="apiso:BoundingBox",
    ),
    CswQueryable(
        "apiso:CRS", Record.crs,
        xpath='concat("urn:ogc:def:crs:","gmd:referenceSystemInfo/'
              'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
              'gmd:RS_Identifier/gmd:codeSpace/gco:CharacterString",":'
              '","gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:'
              'referenceSystemIdentifier/gmd:RS_Identifier/gmd:version/gco:'
              'CharacterString",":","gmd:referenceSystemInfo/'
              'gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/'
              'gmd:RS_Identifier/gmd:code/gco:CharacterString")',
    ),
    CswQueryable(
        "apiso:AlternateTitle", Record.title_alternate,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/"
              "gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:RevisionDate", Record.date_revision,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation'
              '/gmd:CI_Citation/gmd:date/gmd:CI_Date[gmd:dateType/'
              'gmd:CI_DateTypeCode/@codeListValue="revision"]/'
              'gmd:date/gco:Date',
    ),
    CswQueryable(
        "apiso:CreationDate", Record.date_creation,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/'
              'gmd:CI_Citation/gmd:date/gmd:CI_Date[gmd:dateType/'
              'gmd:CI_DateTypeCode/@codeListValue="creation"]/'
              'gmd:date/gco:Date',
    ),
    CswQueryable(
        "apiso:PublicationDate", Record.date_publication,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/'
              'gmd:CI_Citation/gmd:date/gmd:CI_Date[gmd:dateType/'
              'gmd:CI_DateTypeCode/@codeListValue="publication"]/'
              'gmd:date/gco:Date',
    ),
    CswQueryable(
        "apiso:OrganisationName", Record.organization,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
              'gmd:organisationName/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:HasSecurityConstraints", Record.securityconstraints,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:resourceConstraints/gmd:MD_SecurityConstraints",
    ),
    CswQueryable(
        "apiso:Language", Record.language,
        xpath="gmd:language/gmd:LanguageCode|gmd:language/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:ParentIdentifier", Record.parentidentifier,
        xpath="gmd:parentIdentifier/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:KeywordType", Record.keywordtype,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:descriptiveKeywords/gmd:MD_Keywords/gmd:type/"
              "gmd:MD_KeywordTypeCode",
    ),
    CswQueryable(
        "apiso:TopicCategory", Record.topicategory,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:topicCategory/gmd:MD_TopicCategoryCode",
    ),
    CswQueryable(
        "apiso:ResourceLanguage", Record.resourcelanguage,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/"
              "gmd:CI_Citation/gmd:identifier/gmd:code/"
              "gmd:MD_LanguageTypeCode",
    ),
    CswQueryable(
        "apiso:GeographicDescriptionCode", Record.geodescode,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/"
              "gmd:EX_Extent/gmd:geographicElement/"
              "gmd:EX_GeographicDescription/gmd:geographicIdentifier/"
              "gmd:MD_Identifier/gmd:code/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:Denominator", Record.denominator,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:spatialResolution/gmd:MD_Resolution/gmd:equivalentScale/"
              "gmd:MD_RepresentativeFraction/gmd:denominator/gco:Integer",
    ),
    CswQueryable(
        "apiso:DistanceValue", Record.distancevalue,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/"
              "gco:Distance",
    ),
    CswQueryable(
        "apiso:DistanceUOM", Record.distanceuom,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/"
              "gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/"
              "gco:Distance/@uom",
    ),
    CswQueryable(
        "apiso:TempExtent_begin", Record.time_begin,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/"
              "gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/"
              "gmd:extent/gml:TimePeriod/gml:beginPosition",
    ),
    CswQueryable(
        "apiso:TempExtent_end", Record.time_end,
        xpath="gmd:identificationInfo/gmd:MD_DataIdentification/gmd:extent/"
              "gmd:EX_Extent/gmd:temporalElement/gmd:EX_TemporalExtent/"
              "gmd:extent/gml:TimePeriod/gml:endPosition",
    ),
    CswQueryable(
        "apiso:AnyText", Record.anytext,
        xpath="//",
    ),
    CswQueryable(
        "apiso:ServiceType", Record.servicetype,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:serviceType/gco:LocalName",
    ),
    CswQueryable(
        "apiso:ServiceTypeVersion", Record.servicetypeversion,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:serviceTypeVersion/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:Operation", Record.operation,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:containsOperations/srv:SV_OperationMetadata/"
              "srv:operationName/gco:CharacterString",
    ),
    CswQueryable(
        "apiso:CouplingType", Record.couplingtype,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:couplingType/srv:SV_CouplingType",
    ),
    CswQueryable(
        "apiso:OperatesOn", Record.operateson,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:operatesOn/gmd:MD_DataIdentification/gmd:citation/"
              "gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:code/"
              "gco:CharacterString",
    ),
    CswQueryable(
        "apiso:OperatesOnIdentifier", Record.operatesonidentifier,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:coupledResource/srv:SV_CoupledResource/srv:identifier/"
              "gco:CharacterString",
    ),
    CswQueryable(
        "apiso:OperatesOnName", Record.operatesoname,
        xpath="gmd:identificationInfo/srv:SV_ServiceIdentification/"
              "srv:coupledResource/srv:SV_CoupledResource/srv:operationName/"
              "gco:CharacterString",
    ),
]
