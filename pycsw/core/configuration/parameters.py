class ContextModelParameter(object):
    name = ""
    values = []

    def __init__(self, name, values):
        self.name = name
        self.values = values


accept_versions = ContextModelParameter("acceptVersions", ["2.0.2", "3.0.0"])
accept_formats = ContextModelParameter(
    "acceptFormats", ["text/xml", "application/xml"])
typename = ContextModelParameter("typeName", ["csw:Record"])
typenames = ContextModelParameter("typeNames", ["csw:Record"])

version = ContextModelParameter("version", ["2.0.2", "3.0.0"])
service = ContextModelParameter("service", ["CSW"])
max_record_default = ContextModelParameter("MaxRecordDefault", ["10"])
post_encoding = ContextModelParameter("PostEncoding", ["XML", "SOAP"])
xpath_queryables = ContextModelParameter("XPathQueryables", ["allowed"])
output_format = ContextModelParameter(
    "outputFormat", ["application/xml", "application/json"])
result_type = ContextModelParameter(
    'resultType', ['hits', 'results', 'validate'])

output_schema = ContextModelParameter(
    'outputSchema', ['http://www.opengis.net/cat/csw/2.0.2'])
output_schema_csw3 = ContextModelParameter(
    'outputSchema', ['http://www.opengis.net/cat/csw/3.0'])

constraint_language = ContextModelParameter(
    'CONSTRAINTLANGUAGE', ['FILTER', 'CQL_TEXT'])
element_set_name = ContextModelParameter(
    'ElementSetName',['brief', 'summary', 'full'])
sections = ContextModelParameter(
    "sections",
    [
        "ServiceIdentification",
        "ServiceProvider",
        "OperationsMetadata",
        "Filter_Capabilities"
    ]
)
schema_language = ContextModelParameter(
    "schemaLanguage",
    [
        'http://www.w3.org/XML/Schema',
        'http://www.w3.org/TR/xmlschema-1/',
        'http://www.w3.org/2001/XMLSchema'
    ]
)

sections_csw3 = ContextModelParameter(
    "sections",
    [
        "ServiceIdentification",
        "ServiceProvider",
        "OperationsMetadata",
        "Filter_Capabilities",
        "All",
    ]
)
output_format_csw3 = ContextModelParameter(
    "outputFormat", ["application/xml", "application/json",
                     "application/atom+xml"])

open_search = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/OpenSearch', [True])
get_capabilities_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetCapabilities-XML', [True])
get_record_by_id_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecordById-XML', [True])
get_records_basic_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecords-Basic-XML', [True])
get_records_distributed_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecords-Distributed-XML',
    [True]
)
get_records_distributed_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecords-Distributed-KVP',
    [True]
)
get_records_async_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecords-Async-XML', [True])
get_records_async_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetRecords-Async-KVP', [True])
get_domain_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetDomain-XML', [True])
get_domain_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/GetDomain-KVP', [True])
transaction = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Transaction', [True])
harvest_basic_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Basic-XML', [True])
harvest_basic_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Basic-KVP', [True])
harvest_async_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Async-XML', [True])
harvest_async_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Async-KVP', [True])
harvest_periodic_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Periodic-XML', [True])
harvest_periodic_kvp = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Harvest-Periodic-KVP', [True])
filter_cql = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Filter-CQL', [True])
filter_fes_xml = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Filter-FES-XML', [True])
filter_fes_kvp_advanced = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/Filter-FES-KVP-Advanced', [True])
supported_gml_versions = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/SupportedGMLVersions',
    ["http://www.opengis.net/gml"]
)
default_sorting_algorithm = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/DefaultSortingAlgorithm', [True])
core_queryables = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/CoreQueryables', [True])
core_sortables = ContextModelParameter(
    'http://www.opengis.net/spec/csw/3.0/conf/CoreSortables', [True])
