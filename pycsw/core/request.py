"""A custom Request class for pycsw

# proposed WSGI app
def application(env, start_response):
    config = env.get("PYCSW_CONFIG")  # or get the config from QUERY_STRING
    server = pycsw.server.PycswServer(env=env, rtconfig=config)
    request = PycswRequest(**env)
    response, http_code, response_headers  = server.dispatch(request)

"""

class PycswRequest(object):

    def __init__(self, **request_environment):
        # FIXME - investigate WSGI environment variables
        self.method = request_environment["METHOD"]
