"""Integration tests for pycsw.pycswserver module."""

import pytest

from pycsw import pycswserver
from pycsw import httprequest
from pycsw.services.csw import cswbase


@pytest.mark.integration
class TestPycswServer:

    def test_setup_csw202_service_default_config(self):
        csw202_service = pycswserver.PycswServer.setup_csw202_service()
        assert csw202_service.name == "CSW"
        assert csw202_service.version == "2.0.2"
        assert csw202_service.identifier == "CSW_v2.0.2"

    def test_default_csw_service(self):
        server = pycswserver.PycswServer()
        assert server.default_csw_service.version == "2.0.2"

    def test_get_schema_processor_csw_kvp_get_capabilities_request(self):
        server = pycswserver.PycswServer()
        params = {
            "service": "CSW",
            "request": "GetCapabilities",
        }
        request = httprequest.PycswHttpRequest(method=httprequest.HttpVerb.GET,
                                               parameters=params,
                                               content_type="")
        schema_processor = server.get_schema_processor(request)
        assert isinstance(schema_processor, cswbase.CswKvpSchemaProcessor)

    def test_get_schema_processor_csw_post_get_capabilities(self):
        body = """
        <?xml version="1.0" encoding="UTF-8"?>
        <GetCapabilities
            xmlns="http://www.opengis.net/cat/csw/2.0.2"
            xmlns:ows="http://www.opengis.net/ows"
            service="CSW">
        </GetCapabilities>
        """.strip()
        request = httprequest.PycswHttpRequest(
            method=httprequest.HttpVerb.POST, body=body.encode())
        server = pycswserver.PycswServer()
        schema_processor = server.get_schema_processor(request)
        assert isinstance(schema_processor,
                          cswbase.CswContentTypeSchemaProcessor)

    def test_process_request_csw_kvp_get_capabilities_request(self):
        server = pycswserver.PycswServer()
        params = {
            "service": "CSW",
            "request": "GetCapabilities",
        }
        request = httprequest.PycswHttpRequest(method=httprequest.HttpVerb.GET,
                                               parameters=params,
                                               content_type="")
        schema_processor = server.get_schema_processor(request)
        response = schema_processor.process_request(request)
