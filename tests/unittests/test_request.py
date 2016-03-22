"""Unit tests for pycsw.request."""

from wsgiref.util import setup_testing_defaults

import pytest

from pycsw import request


@pytest.mark.unit
class TestRequest(object):

    def test_request_creation(self):
        fake_env = {}
        setup_testing_defaults(fake_env)
        fake_path = "/fake/path/"
        fake_params = {
            "param1": "value1",
            "param2": "value2",
        }
        fake_env["PATH_INFO"] = "/fake/path/?{}".format(
            "&".join(("{}={}".format(k, v) for k,v in fake_params.items())))
        req = request.PycswHttpRequest(**fake_env)
        assert req.scheme == "http"
        assert req.path == fake_path
