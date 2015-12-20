"""A custom Request class for pycsw

# proposed WSGI app
def application(env, start_response):
    config = env.get("PYCSW_CONFIG")  # or get the config from QUERY_STRING
    server = pycsw.server.PycswServer(env=env, rtconfig=config)
    request = PycswRequest(**env)
    response, http_code, response_headers  = server.dispatch(request)

"""

import logging
import urlparse
import cgi
import StringIO
import wsgiref.util
import re

from . import util

LOGGER = logging.getLogger(__name__)


class PycswHttpRequest(object):

    def __init__(self, **request_environment):
        """A class to manage incoming HTTP requests

        This is loosely modelled after django's HttpRequest API
        """

        self.scheme = wsgiref.util.guess_scheme(request_environment)
        self.path = wsgiref.util.request_uri(request_environment)
        self.META = self._get_http_headers(**request_environment)
        in_fh = request_environment.get("wsgi.input", StringIO.StringIO())
        self.body = in_fh.read(self.META["HTTP_CONTENT_LENGTH"])
        self.GET = self._get_query_string(
            request_environment.get("QUERY_STRING", ""))
        self.POST = self._get_query_string(self.body)
        self.method = request_environment.get("REQUEST_METHOD", "")

    def _get_query_string(self, raw_query_string):
        query_string_dict = urlparse.parse_qs(raw_query_string)
        parsed = {}
        for key, values in query_string_dict.items():
            parsed[key.lower()] = [cgi.escape(v) for v in values]
        return parsed

    def _get_http_headers(self, **raw_request):
        request = raw_request.copy()
        headers = {}
        for key, value in request.items():
            parsed_key = "HTTP_{}".format(key.upper().replace("-", "_"))
            headers[parsed_key] = value
        try:
            content_length = int(request.get("CONTENT_LENGTH", 0))
        except ValueError:
            content_length = 0
        headers["HTTP_CONTENT_LENGTH"] = content_length
        headers["HTTP_ACCEPT"] = [word.strip() for word in
                                  headers.get("HTTP_ACCEPT", "").split(",")]
        return headers

