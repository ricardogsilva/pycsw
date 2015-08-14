# -*- coding: iso-8859-15 -*-
# =================================================================
#
# Authors: Adam Hinz <hinz.adam@gmail.com>
#
# Copyright (c) 2015 Adam Hinz
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

# WSGI wrapper for pycsw
#
# Apache mod_wsgi configuration
#
# ServerName host1
# WSGIDaemonProcess host1 home=/var/www/pycsw processes=2
# WSGIProcessGroup host1
#
# WSGIScriptAlias /pycsw-wsgi /var/www/pycsw/csw.wsgi
#
# <Directory /var/www/pycsw>
#  Order deny,allow
#  Allow from all
# </Directory>
#
# or invoke this script from the command line:
#
# $ python ./csw.wsgi
#
# which will publish pycsw to:
#
# http://localhost:8000/
#

from StringIO import StringIO
import gzip
import os
import sys
import urlparse

from pycsw.server import CswServer


def application(environment, start_response):
    """Pycsw WSGI wrapper and entry point."""
    request = PycswHttpRequest(environment)
    config = request.query.get("config", os.environ.get("PYCSW_CONFIG"))
    csw_server = CswServer(rtconfig=config)
    status, response_headers, response_body = csw_server.dispatch(request)
    # status, response_headers, response_body = check_env(environment)
    if request.gzip:
        response_headers["Content-Encoding"] = "gzip"
        level = csw_server.context.settings["server"]["gzip_compresslevel"]
        response_body = gzip_response(level, response_body)
    response_headers["Content-Length"] = str(len(response_body))
    start_response(status, response_headers)
    return [response_body]


def gzip_response(compression, response_body):
    """Compress the response body"""
    if compression > 0:
        compression = compression if compression <= 9 else 9
        temp_buffer = StringIO()
        with gzip.open("", "wb", compression, temp_buffer) as gzip_handler:
            gzip_handler.write(response_body)
        result = temp_buffer.getvalue()
    else:
        result = response_body
    return result


class PycswHttpRequest(object):
    path = ""
    accept = "*/*"
    gzip = False
    method = None
    text = ""
    query = dict()

    def __init__(self, environment):
        """Utility class to facilitate working with raw HTTTP requests."""
        self.method = environment["REQUEST_METHOD"]
        self.path = environment["PATH_INFO"]
        self.accept = environment["HTTP_ACCEPT"]
        accept_encoding = environment.get("HTTP_ACCEPT_ENCODING")
        if accept_encoding is not None and "gzip" in accept_encoding:
            self.gzip = True
        request_body = ""
        if self.method == "GET":
            self.query = urlparse.parse_qs(environment["QUERY_STRING"])
        elif self.method == "POST":
            try:
                request_body_size = int(environment.get("CONTENT_LENGTH", 0))
            except ValueError:
                request_body_size = 0
            request_body = environment["wsgi.input"].read(request_body_size)
            self.query = urlparse.parse_qs(request_body)
        if len(self.query) == 0:
            self.text = request_body


def check_env(environment):
    """A test function"""
    response_body = ["{}: {}".format(k, v) for k, v in environment.iteritems()]
    response_body = "\n".join(response_body)
    status = "200 OK"
    response_headers = [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(response_body)))
    ]
    return status, response_headers, response_body


if __name__ == '__main__':  # run inline using WSGI reference implementation
    from wsgiref.simple_server import make_server
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = make_server("", port, application)
    print("Serving on port {}...".format(port))
    httpd.serve_forever()
