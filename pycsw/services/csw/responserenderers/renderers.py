from pyxb.bundles.opengis import csw_2_0_2
from pyxb import BIND

from ...servicebase import ResponseRenderer

class OgcCswXmlRenderer(ResponseRenderer):
    output_format = "text/xml"
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

    def render(self, operation_name, **response):
        func = {
            "GetCapabilities": self.render_capabilities_pyxb
        }[operation_name]
        response_headers = {
            "Content-Type": self.output_format
        }
        return func(**response), response_headers

    def render_capabilities_pyxb(self, **response):
        identification = response["ServiceIdentification"]
        provider = response["ServiceProvider"]
        capabilities = csw_2_0_2.Capabilities(
            version=self.service.version,
            updateSequence=response.get("updateSequence"),
            ServiceIdentification=BIND(
                Title=identification["Title"],
                Abstract=identification["Abstract"],
                Keywords=identification["Keywords"],
                ServiceType=self.service.name,
                ServiceTypeVersion=identification["ServiceTypeVersion"],
                Fees=identification["Fees"],
                AccessConstraints=identification["AccessConstraints"],
            ),
            ServiceProvider=BIND(
                ProviderName=provider["ProviderName"],
                ProviderSite=BIND(href=provider["ProviderSite"]["linkage"]),
                ServiceContact=BIND()  # TODO: Add the remaining elements
            ),
            OperationsMetadata=BIND(),
            Filter_Capabilities=BIND()
        )
        #rendered = capabilities.toxml(encoding="utf-8")
        #return rendered
        return capabilities  # for testign only

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
