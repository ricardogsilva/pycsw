"""Some small tests for aiding development"""

from urllib.parse import parse_qs

import pytest
import requests

@pytest.mark.functional
class TestSuites:

    def test_suites_post(self, test_local_server, test_request,
                         expected_result):
        with open(str(expected_result), mode="r",
                  encoding="utf-8") as expected_fh:
            expected = expected_fh.read()
        with open(str(test_request), encoding="utf-8") as request_fh:
            request_data = request_fh.read()
        response = requests.post(test_local_server, data=request_data)
        assert self._validate_response(expected, response.text)

    def test_suites_get(self, test_local_server, test_request_parameters,
                        expected_result):
        with open(str(expected_result), mode="r",
                  encoding="utf-8") as expected_fh:
            expected = expected_fh.read()
        payload = parse_qs(test_request_parameters)
        response = requests.get(test_local_server, params=payload)
        assert self._validate_response(expected, response.text)

    def _validate_response(self, expected, gotten):
        raise NotImplementedError
