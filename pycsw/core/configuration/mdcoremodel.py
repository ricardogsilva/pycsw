class MdCoreModel(object):
    typename = ""
    outputschema = ""
    mappings = dict()

    def __init__(self, typename, outputschema, mappings):
        self.typename = typename
        self.outputschema = outputschema
        self.mappings = mappings


md_core_model = MdCoreModel(
    "pycsw:CoreMetadata",
    "http://pycsw.org/metadata",
    {
        'pycsw:Identifier': 'identifier',
        # CSW typename (e.g. csw:Record, md:MD_Metadata)
        'pycsw:Typename': 'typename',
        # schema namespace, i.e. http://www.isotc211.org/2005/gmd
        'pycsw:Schema': 'schema',
        # origin of resource, either 'local', or URL to web service
        'pycsw:MdSource': 'mdsource',
        # date of insertion
        'pycsw:InsertDate': 'insert_date',  # date of insertion
        # raw XML metadata
        'pycsw:XML': 'xml',
        # bag of metadata element and attributes ONLY, no XML tages
        'pycsw:AnyText': 'anytext',
        'pycsw:Language': 'language',
        'pycsw:Title': 'title',
        'pycsw:Abstract': 'abstract',
        'pycsw:Keywords': 'keywords',
        'pycsw:KeywordType': 'keywordstype',
        'pycsw:Format': 'format',
        'pycsw:Source': 'source',
        'pycsw:Date': 'date',
        'pycsw:Modified': 'date_modified',
        'pycsw:Type': 'type',
        # geometry, specified in OGC WKT
        'pycsw:BoundingBox': 'wkt_geometry',
        'pycsw:CRS': 'crs',
        'pycsw:AlternateTitle': 'title_alternate',
        'pycsw:RevisionDate': 'date_revision',
        'pycsw:CreationDate': 'date_creation',
        'pycsw:PublicationDate': 'date_publication',
        'pycsw:OrganizationName': 'organization',
        'pycsw:SecurityConstraints': 'securityconstraints',
        'pycsw:ParentIdentifier': 'parentidentifier',
        'pycsw:TopicCategory': 'topicategory',
        'pycsw:ResourceLanguage': 'resourcelanguage',
        'pycsw:GeographicDescriptionCode': 'geodescode',
        'pycsw:Denominator': 'denominator',
        'pycsw:DistanceValue': 'distancevalue',
        'pycsw:DistanceUOM': 'distanceuom',
        'pycsw:TempExtent_begin': 'time_begin',
        'pycsw:TempExtent_end': 'time_end',
        'pycsw:ServiceType': 'servicetype',
        'pycsw:ServiceTypeVersion': 'servicetypeversion',
        'pycsw:Operation': 'operation',
        'pycsw:CouplingType': 'couplingtype',
        'pycsw:OperatesOn': 'operateson',
        'pycsw:OperatesOnIdentifier': 'operatesonidentifier',
        'pycsw:OperatesOnName': 'operatesoname',
        'pycsw:Degree': 'degree',
        'pycsw:AccessConstraints': 'accessconstraints',
        'pycsw:OtherConstraints': 'otherconstraints',
        'pycsw:Classification': 'classification',
        'pycsw:ConditionApplyingToAccessAndUse': 'conditionapplyingtoaccessanduse',
        'pycsw:Lineage': 'lineage',
        'pycsw:ResponsiblePartyRole': 'responsiblepartyrole',
        'pycsw:SpecificationTitle': 'specificationtitle',
        'pycsw:SpecificationDate': 'specificationdate',
        'pycsw:SpecificationDateType': 'specificationdatetype',
        'pycsw:Creator': 'creator',
        'pycsw:Publisher': 'publisher',
        'pycsw:Contributor': 'contributor',
        'pycsw:Relation': 'relation',
        # links: format "name,description,protocol,url[^,,,[^,,,]]"
        'pycsw:Links': 'links',
    }
)
