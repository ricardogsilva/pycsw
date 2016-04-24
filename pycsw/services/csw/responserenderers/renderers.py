from ...servicebase import ResponseRenderer

class OgcCswXmlRenderer(ResponseRenderer):
    output_format = "application/xml"
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

    def render(self, response):
        # could use pyxb to render into XML
        # or maybe a jinja2 template
        raise NotImplementedError
