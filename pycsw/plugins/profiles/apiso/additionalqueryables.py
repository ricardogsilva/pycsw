"""
Additional ISO queryables for the apiso profile
"""

from ....core.configuration.queryables import CswQueryable
from ....core.models import Record


queryables = [
    CswQueryable(
        "apiso:Degree", Record.degree,
        xpath='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
              'gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/'
              'gmd:pass/gco:Boolean',
    ),
    CswQueryable(
        "apiso:AccessConstraints", Record.accessconstraints,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
              'gmd:accessConstraints/gmd:MD_RestrictionCode',
    ),
    CswQueryable(
        "apiso:OtherConstraints", Record.otherconstraints,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
              'gmd:otherConstraints/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:Classification", Record.classification,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:resourceConstraints/gmd:MD_LegalConstraints/'
              'gmd:accessConstraints/gmd:MD_ClassificationCode',
    ),
    CswQueryable(
        "apiso:ConditionApplyingToAccessAndUse",
        Record.conditionapplyingtoaccessanduse,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:useLimitation/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:Lineage", Record.lineage,
        xpath='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:lineage/'
              'gmd:LI_Lineage/gmd:statement/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:ResponsiblePartyRole", Record.responsiblepartyrole,
        xpath='gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode',
    ),
    CswQueryable(
        "apiso:SpecificationTitle", Record.specificationtitle,
        xpath='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
              'gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/'
              'gmd:specification/gmd:CI_Citation/gmd:title/'
              'gco:CharacterString',
    ),
    CswQueryable(
        "apiso:SpecificationDate", Record.specificationdate,
        xpath='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
              'gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/'
              'gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/'
              'gmd:date/gco:Date',
    ),
    CswQueryable(
        "apiso:SpecificationDateType", Record.specificationdatetype,
        xpath='gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/'
              'gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/'
              'gmd:specification/gmd:CI_Citation/gmd:date/gmd:CI_Date/'
              'gmd:dateType/gmd:CI_DateTypeCode',
    ),
    CswQueryable(
        "apiso:Creator", Record.creator,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
              'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
              '@codeListValue="originator"]/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:Publisher", Record.publisher,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
              'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
              '@codeListValue="publisher"]/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:Contributor", Record.contributor,
        xpath='gmd:identificationInfo/gmd:MD_DataIdentification/'
              'gmd:pointOfContact/gmd:CI_ResponsibleParty/'
              'gmd:organisationName[gmd:role/gmd:CI_RoleCode/'
              '@codeListValue="contributor"]/gco:CharacterString',
    ),
    CswQueryable(
        "apiso:Relation", Record.relation,
        xpath='gmd:identificationInfo/gmd:MD_Data_Identification/'
              'gmd:aggregationInfo',
    ),
]
