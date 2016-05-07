from jinja2 import Environment
from jinja2 import PackageLoader

from ...servicebase import ResponseRenderer

class OgcCswXmlRenderer(ResponseRenderer):
    output_format = "text/xml"
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

    def __init__(self):
        super().__init__()
        self.template_environment = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=PackageLoader("pycsw",
                                 "services/csw/responserenderers/templates"),
        )

    def render(self, operation_name, **response):
        # could use pyxb to render into XML
        # or maybe a jinja2 template
        func = {
            "GetCapabilities": self.render_capabilities
        }[operation_name]
        return func(**response)

    def render_capabilities(self, namespaces=None, **response):
        template = self.template_environment.get_template("capabilities.xml")
        rendered = template.render(
            namespaces=namespaces if namespaces is not None else {},
            **response
        )
        return rendered

    def can_render(self, operation, request):
        if operation.name == "GetCapabilities":
            for output_format in operation.accept_formats:
                if output_format == self.output_format:
                    result = True
                    break
            else:
                result = self._can_render_http_header(operation,
                                                      request.accept)
        else:
            # compare the outputFormat and outputSchema parameters
            # also call out to the _can_render_http_header() method
            raise NotImplementedError
        return result

    def _can_render_http_header(self, operation, http_accept_header):
        raise NotImplementedError
