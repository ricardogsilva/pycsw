"""Unit tests for pycsw.operations.csw.getcapabilities"""

import pytest

from pycsw.operations.csw import getcapabilities
from pycsw.httprequest import HttpVerb


@pytest.mark.unit
class TestGetCapabilities202OperationProcessor:

    def test_creation_good_parameters(self):
        accept_versions = ["some version", "another version"]
        sections = ["All"]
        accept_formats = ["format1", "format2"]
        update_sequence = 0
        enabled = True
        allowed_http_verbs = [HttpVerb.GET, HttpVerb.POST]
        processor = getcapabilities.GetCapabilities202OperationProcessor(
            accept_versions=accept_versions,
            sections=sections,
            accept_formats=accept_formats,
            update_sequence=update_sequence,
            enabled=enabled,
            allowed_http_verbs=allowed_http_verbs
        )
        assert processor.name == "GetCapabilities"
        assert processor.enabled == enabled
        assert all([v in processor.allowed_http_verbs for v in
                    allowed_http_verbs])
        assert processor.accept_versions == accept_versions
        assert processor.sections == sections
        assert processor.accept_formats == accept_formats

    def test_creation_invalid_sections(self):
        with pytest.raises(ValueError):
            processor = getcapabilities.GetCapabilities202OperationProcessor(
                sections=["fake"])
        with pytest.raises(ValueError):
            processor = getcapabilities.GetCapabilities202OperationProcessor(
                sections="fake")
        with pytest.raises(TypeError):
            processor = getcapabilities.GetCapabilities202OperationProcessor(
                sections=1000)
