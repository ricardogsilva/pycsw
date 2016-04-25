from jinja2 import Environment
from jinja2 import PackageLoader

from ...servicebase import ResponseRenderer

class OgcCswXmlRenderer(ResponseRenderer):
    output_format = "application/xml"
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

    def __init__(self):
        super().__init__()
        self.template_environment = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=PackageLoader("pycsw",
                                 "services/csw/responserenderers/templates"),
        )

    def render(self, element=None, **response):
        # could use pyxb to render into XML
        # or maybe a jinja2 template
        func = {
            "Capabilities": self.render_capabilities
        }[element]
        return func(**response)

    def render_capabilities(self, namespaces=None, **response):
        template = self.template_environment.get_template("capabilities.xml")
        rendered = template.render(
            namespaces=namespaces if namespaces is not None else {},
            **response
        )
        return rendered
