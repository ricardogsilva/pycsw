"""A custom Request class for pycsw

"""

import logging
from urllib.parse import parse_qs
import cgi
from io import StringIO
import wsgiref.util
from lxml import etree
import json

from .xmlparser import get_parser

logger = logging.getLogger(__name__)


class PycswHttpRequest(object):

    def __init__(self, **environ):
        """Manage incoming HTTP requests.

        This is loosely modelled after django's HttpRequest API, with some
        additions.

        Parameters
        ----------

        request_environment:
        """

        self.scheme = wsgiref.util.guess_scheme(environ)
        self.path = wsgiref.util.application_uri(environ)
        self.META = self._get_http_headers(**environ)
        content_type, encoding = self._get_content_type(
            self.META.get("HTTP_CONTENT_TYPE", ""))
        self.content_type = content_type
        self.encoding = encoding
        in_fh = environ.get("wsgi.input", StringIO())
        self.body = in_fh.read(self.META["HTTP_CONTENT_LENGTH"])
        self.GET = self._get_query_string(environ.get("QUERY_STRING", ""))
        self.POST = self._get_query_string(self.body)
        self.method = environ.get("REQUEST_METHOD", "")
        self._exml = None
        self._json = None

    @property
    def exml(self):
        if self._exml is None:
            try:
                parser = get_parser(encoding=self.encoding)
                self._exml = etree.fromstring(self.body, parser=parser)
            except etree.XMLSyntaxError:
                logger.debug("Could not extract an xml etree element "
                             "from request")
        return self._exml

    @property
    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self.body, encoding=self.encoding)
            except json.JSONDecodeError:
                logger.debug("Could not extract a json object from request")
        return self._json


    def _get_query_string(self, raw_query_string):
        query_string_dict = parse_qs(raw_query_string, encoding=self.encoding)
        parsed = {}
        for key, values in query_string_dict.items():
            parsed[key.lower()] = [cgi.escape(v) for v in values]
        return parsed

    def _get_http_headers(self, **environ):
        request = environ.copy()
        headers = {}
        for key, value in request.items():
            parsed_key = "HTTP_{}".format(key.upper().replace("-", "_"))
            headers[parsed_key] = value
        try:
            content_length = int(request.get("CONTENT_LENGTH", 0))
        except ValueError:
            content_length = 0
        headers["HTTP_CONTENT_LENGTH"] = content_length
        accept_headers = [word.strip() for word in
                          headers.get("HTTP_ACCEPT", "").split(",")]
        headers["HTTP_ACCEPT"] = accept_headers if any(accept_headers) else []
        return headers

    def _get_content_type(self, content_type_header):
        parts = content_type_header.split(";")
        content_type = parts[0]
        encoding = "utf-8"
        for param in parts[1:]:
            name, value = param.split("=")
            if name.lower() == "charset":
                encoding = value
        return content_type, encoding
