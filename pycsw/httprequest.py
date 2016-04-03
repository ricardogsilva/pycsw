"""A custom Request class for pycsw.

"""

import logging
import json
import enum

from lxml import etree

from .xmlparser import get_parser

logger = logging.getLogger(__name__)


class HttpVerb(enum.Enum):
    GET = 1
    POST = 2
    PUT = 3
    PATCH = 4
    HEAD = 5
    DELETE = 6
    OPTIONS = 7


class PycswHttpRequest:
    """Wrapper for HTTP requests.

    This class defines a uniform request type that is used to feed requests
    to pycsw server. Client code can receive incoming requests from a myriad
    of sources (standalone WSGI, werkzeug, django, etc.). By using this class
    there is a standard way of supplying pycsw with requests.

    Parameters
    ----------
    method: HttpVerb
        HTTP method used for making the request.
    parameters: dict, optional
        Query string parameters passed in GET requests.
    form_data: dict, optional
        Key-value pairs passed as form data in POST requests.
    body: str, optional
        Raw request body for requests that are neither GET nor POST with forms.
    username: str, optional
        Name of the user that made the request.
    content_type: str, optional
        The content-type of the request.
    encoding: str, optional
        The request's charset.
    accept: list, optional
        Content-types accepted as a response to the request.

    Attributes
    ----------
    json
    exml

    """

    method = None
    parameters = {}
    form_data = {}
    body = ""
    username = ""
    content_type = "application/xml"
    encoding = "utf-8"
    accept = []
    _json = None
    _exml = None

    def __init__(self, method, parameters=None, form_data=None, body="",
                 username="", content_type="application/xml",
                 encoding="utf-8", accept=None):
        self.method = method
        self.parameters = parameters or {}
        self.form_data = form_data or {}
        self.body = body
        self.username = username
        self.content_type = content_type
        self.encoding = encoding
        self.accept = accept or []
        self._json = None
        self._exml = None

    @property
    def json(self):
        """Parse request body as json.

        Returns
        -------
        json: dict
            The parsed JSON data

        Raises
        ------
        json.JSONDecodeError
            If the request's body cannot be parsed as JSON

        """
        if self._json is None:
            self._json = json.loads(self.body, encoding=self.encoding)
        return self._json

    @property
    def exml(self):
        """Parse request body as XML.

        Returns
        -------
        exml: etree.Element
            The parsed XML data

        Raises
        ------
        etree.XMlSyntaxError
            If the request's body cannot be parsed as XML

        """
        if self._exml is None:
            parser = get_parser(encoding=self.encoding)
            self._exml = etree.fromstring(self.body, parser=parser)
        return self._exml
