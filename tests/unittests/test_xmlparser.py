"""Unit tests for pycsw.xmlparser."""

from unittest import mock

import pytest

from pycsw import xmlparser


@pytest.mark.unit
def test_get_parser_no_schema():
    fake_encoding = "fake_encoding"
    with mock.patch("pycsw.xmlparser.etree.XMLParser", autospec=True) as mocked:
        xmlparser.get_parser(encoding=fake_encoding)
        mocked.assert_called_with(encoding=fake_encoding,
                                  resolve_entities=False,
                                  schema=None)
