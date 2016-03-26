from .. import csw
from ..operations import base
from ....httprequest import HttpVerb

csw_schema_processor = csw.CswSchemaProcessor(
    namespace="http://www.opengis.net/cat/csw/2.0.2",
    type_names=["csw:Record"],
    record_mapping={
        "title": "dc:title",
        "creator": "dc:creator",
        "subject": "dc:subject",
        "abstract": "dct:abstract",
        "publisher": "dc:publisher",
        "contributor": "dc:contributor",
        "modified": "dct:modified",
        "type_": "dc:type",
        "format_": "dc:format",
        "identifier": "dc:identifier",
        "source": "dc:source",
        "language": "dc:language",
        "association": "dc:relation",
        "bounding_box": "ows:BoundingBox",
        "rights": "dc:rights",
    },
    element_set_names={
        "full": [
            "dc:identifier",
            "dc:title",
            "dc:creator",
            "dc:subject",
            "dct:abstract",
            "dc:publisher",
            "dc:contributor",
            "dct:modified",
            "dc:type",
            "dc:format",
            "dc:source",
            "dc:language",
            "dc:relation",
            "ows:BoundingBox",
            "dc:rights",
        ],
        "summary": [
            "dc:identifier",
            "dc:title",
            "dc:type",
            "dc:subject",
            "dc:format",
            "dc:relation",
            "dct:modified",
            "dct:abstract",
            "dct:spatial",  # ?
            "ows:BoundingBox",
        ],
        "brief": [
            "dc:identifier",
            "dc:title",
            "dc:type",
            "ows:BoundingBox",
        ],
    }
)

xml_content_type = csw.CswContentTypeProcessor(
    media_type="application/xml",
    namespaces={
        "csw": "http://www.opengis.net/cat/csw/2.0.2",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dct": "http://purl.org/dc/terms/",
        "ows": "http://www.opengis.net/ows",
    },
    accepted_schemas=[
        csw_schema_processor,
    ]
)

get_capabilities = base.GetCapabilities202Operation(
    enabled=True,
    allowed_http_verbs=[
        HttpVerb.GET,
    ]
)

csw202_service = csw.Csw202Service(
    enabled=True,
    distributed_search=csw.CswDistributedSearch(),
    operations=[
        get_capabilities,
    ],
    content_types=[
        xml_content_type,
    ]
)
