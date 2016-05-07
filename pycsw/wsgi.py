"""Pycsw default wsgi application.

To use this in production be sure to read gunicorn's documentation[1]

For development and testing, you can get pycsw up and running with:

.. code::

   gunicorn -w 2 --logfile=- --reload pycsw.wsgi:application

"""

import logging

from werkzeug.wrappers import Request
from werkzeug.wrappers import Response

from . import httprequest
from . import server
from . import exceptions

logger = logging.getLogger(__name__)


@Request.application
def application(request):
    logging.basicConfig(level=logging.DEBUG)
    pycsw_request = build_request(request)
    logger.debug("request parameters: {}".format(pycsw_request.parameters))
    pycsw_server = server.PycswServer()
    try:
        schema_processor = pycsw_server.get_schema_processor(pycsw_request)
        operation, parameters = schema_processor.parse_request(pycsw_request)
        operation.prepare(**parameters)
        service = schema_processor.service
        response_renderer = service.get_renderer(operation, pycsw_request)
        response = operation()
        rendered_response = response_renderer.render(operation.name,
                                                     **response)
    except exceptions.PycswError:
        raise
        #response = pycsw_server.generate_error_response(err)
    else:
        werkzeug_response = Response(rendered_response)
        return werkzeug_response


def build_request(werkzeug_request):
    """Convert a werkzeug request into a PycswHttpRequest.

    Parameters
    ----------
    werkzeug_request: werkzeug.wrappers.Request
        The werkzeug request

    Returns
    -------
    pycsw.httprequest.PycswHttpRequest
        The pycsw request.

    """

    args = {k: v[0] for k, v in dict(werkzeug_request.args).items()}
    form_data = {k: v[0] for k, v in dict(werkzeug_request.form).items()}
    request = httprequest.PycswHttpRequest(
        method=httprequest.HttpVerb[werkzeug_request.method],
        parameters=args,
        form_data=form_data,
        body=werkzeug_request.data
    )
    return request
