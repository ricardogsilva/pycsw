"""Unit tests for pycsw.server."""

import pytest
import mock

from pycsw import server

pytestmark = pytest.mark.unit


class TestPycswServer:

    def test_load_config_from_path(self):
        fake_path = "/fake/path"
        fake_contents = {"param1": "value1"}
        with mock.patch("pycsw.server.open", mock.mock_open(), 
                        create=True) as mocked_fh, \
                mock.patch("pycsw.server.yaml", autospec=True) as mocked_yaml:
            mocked_yaml.safe_load.return_value = fake_contents
            result = server.PycswServer._load_config_from_path(fake_path)
            assert result == fake_contents
