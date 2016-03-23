"""Unit tests for pycsw.request."""

import json

from lxml import etree
import pytest

from pycsw import httprequest


@pytest.mark.unit
class TestRequest(object):

    def test_request_get(self):
        verb = httprequest.HttpVerb.GET
        params = {
            "param1": "value1",
            "param2": "value2",
        }
        request = httprequest.PycswHttpRequest(
            method=httprequest.HttpVerb.GET,
            parameters=params
        )
        assert request.method == verb
        assert request.parameters == params

    def test_request_json_post(self):
        verb = httprequest.HttpVerb.POST
        fake_content_type = "fake_content_type"
        json_data = {
            "param1": "value1",
            "param2": "value2",
        }
        request = httprequest.PycswHttpRequest(
            method=verb,
            body=json.dumps(json_data),
            content_type=fake_content_type
        )
        assert request.method == verb
        assert request.content_type == fake_content_type
        assert request.json == json_data

    def test_request_xml_post(self):
        verb = httprequest.HttpVerb.POST
        fake_content_type = "fake_content_type"
        exml = etree.Element("test")
        fake_encoding = "utf-8"
        request = httprequest.PycswHttpRequest(
            method=verb,
            body=etree.tostring(exml, encoding=fake_encoding)
        )
        assert request.method == verb
        assert request.exml.tag == exml.tag
