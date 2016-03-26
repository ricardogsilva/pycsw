"""Pycsw server class."""

import logging


logger = logging.getLogger(__name__)

simpler_config = {
    "encoding": "utf-8",
    "services": [
        "pycsw.services.csw.defaults.csw202.csw202_service",
    ]
}
example_config = {
    "encoding": "utf-8",
    "services": {
        "CSW_v2.0.2": {
            "class_path": "pycsw.services.csw.Csw202Service",
            "enabled": True,
            "distributed_search": {
                "enabled": True,
                "remote_catalogues": [],
                "hop_count": 2,
            },
            "operations": {
                "GetCapabilities": {
                    "enabled": True,
                    "allowed_http_verbs": ["GET", "POST"],
                },
                "GetRecords": {
                    "enabled": True,
                    "allowed_http_verbs": ["GET", "POST"],
                },
            },
            "key_value_pair_configurations": [
                {
                    "name": "OGC CSW kvp",
                },
            ],
            "content_types": [
                {
                    "media_type": "application/xml",
                    "namespaces": {
                        "csw": "http://www.opengis.net/cat/csw/2.0.2",
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "dct": "http://purl.org/dc/terms/",
                        "ows": "http://www.opengis.net/ows",
                    },
                    "schemas": [
                        {
                            "namespace":"http://www.opengis.net/cat/csw/2.0.2",
                            "type_names": ["csw:Record"],
                            "record_mapping": {
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
                            "element_set_names": {
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
                            },
                        },
                        {
                            "namespace": "http://www.isotc211.org/2005/gmd",  # the ISO AP plugin would add stuff here
                        },
                    ]
                }
            ],
            "repositories": {},
            "query_languages": {},
        },
    },
}

class PycswServer:
    """Processes incoming HTTTP requests."""

    services = []

    def __init__(self, config_path=None, **config_args):
        # load common config for all services.
        pass

    def process_request(self, request):
        # call upon the correct service for processing the request
        # catch any errors
        pass
