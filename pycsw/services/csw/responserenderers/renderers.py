from pyxb import BIND
from pyxb.bundles.opengis import csw_2_0_2
from pyxb.bundles.opengis import filter

from ....httprequest import HttpVerb
from ...servicebase import ResponseRenderer

class OgcCswXmlRenderer(ResponseRenderer):
    output_format = "text/xml"
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

    def render(self, operation_name, **response):
        func = {
            "GetCapabilities": self.render_capabilities,
        }[operation_name]
        response_headers = {
            "Content-Type": self.output_format
        }
        return func(**response), response_headers

    def render_capabilities(self, **response):
        identification = response["ServiceIdentification"]
        provider = response["ServiceProvider"]
        contact = provider["ServiceContact"]
        info = contact["ContactInfo"]
        ops = response["OperationsMetadata"]
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
                AccessConstraints=[identification["AccessConstraints"]],
            ),
            ServiceProvider=BIND(
                ProviderName=provider["ProviderName"],
                ProviderSite=BIND(href=provider["ProviderSite"]["linkage"]),
                ServiceContact=BIND(
                    ContactInfo=BIND(
                        Address=BIND(
                            AdministrativeArea=info.get("AdministrativeArea"),
                            City=info.get("City"),
                            Country=info.get("Country"),
                            DeliveryPoint=info.get("DeliveryPoint"),
                            ElectronicMailAddress=info.get(
                                "ElectronicMailAddress"),
                            PostalCode=info.get("PostalCode"),
                        ),
                        ContactInstructions=contact.get("ContactInstructions"),
                        HoursOfService=contact.get("HoursOfService"),
                        OnlineResource=BIND(
                            href=contact.get("OnlineResource")),
                        Phone=contact.get("Phone")
                    ),
                    IndividualName=contact.get("IndividualName"),
                    PositionName=contact.get("PositionName"),
                    Role=contact.get("Role")
                )
            ),
            OperationsMetadata=BIND(
                Operation=[
                    BIND(
                        name=op["name"],
                        DCP=[
                            BIND(HTTP=BIND(
                                Get=[BIND(href=dcp[1]) for dcp in op["DCP"] if
                                     dcp[0] == HttpVerb.GET],
                                Post=[BIND(href=dcp[1]) for dcp in op["DCP"] if
                                      dcp[0] == HttpVerb.POST],
                            ))
                        ],
                        Parameter=[
                            BIND(
                                name=param[0],
                                Value=[str(value) for value in param[1]],
                                Metadata=param[2]
                            ) for param in op["Parameter"]
                        ],
                        Constraint=[
                            BIND(
                                name=constraint[0],
                                Value=[str(value) for value in constraint[1]],
                                Metadata=constraint[2],
                            ) for constraint in op["Constraint"]
                        ],
                        Metadata=None  # reimplement if needed
                    ) for op in ops
                ],
            ),
            Filter_Capabilities=BIND()
        )
        #rendered = capabilities.toxml(encoding="utf-8")
        #return rendered
        return capabilities  # for testing only

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
