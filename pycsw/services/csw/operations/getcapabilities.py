import logging

from .... import parameters
from ....exceptions import CswError
from ....exceptions import INVALID_PARAMETER_VALUE
from ....exceptions import INVALID_UPDATE_SEQUENCE
from ....exceptions import PycswError
from ....exceptions import VERSION_NEGOTIATION_FAILED
from ....httprequest import HttpVerb
from ....operationbase import Operation

logger = logging.getLogger(__name__)


# FIXME - It is kind of lame that section names appear on two different places
class GetCapabilities(Operation):
    """GetCapabilities operation.

    Parameters
    ----------
    Attributes
    ----------
    name: str
        The name of this operation.
    accept_versions: pycsw.operations.parameters.TextListParameter
        This parameter is managed by a descriptor class. It represents the
        versions accepted by pycsw.

    """

    name = "GetCapabilities"

    accept_versions = parameters.TextListParameter(
        "AcceptVersions",
        optional=True
    )
    sections = parameters.TextListParameter(
        "Sections",
        optional=True,
        default=["All"],
        allowed_values=[
            "All",
            "ServiceIdentification",
            "ServiceProvider",
            "OperationsMetadata",
            "Contents",
            "Filter_Capabilities",
        ]
    )
    accept_formats = parameters.TextListParameter(
        "AcceptFormats",
        optional=True
    )
    update_sequence = parameters.IntParameter(
        "updateSequence",
        optional=True,
        allowed_values=[0, 1],
        default=0
    )

    def __init__(self, accept_versions=None, sections=None,
                 accept_formats=None, update_sequence=None, enabled=True,
                 allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        # OGC CSWv2.0.2 mandates that GetCapabilities
        # must accept GET requests
        self.allowed_http_verbs.add(HttpVerb.GET)
        self.accept_versions = accept_versions
        self.sections = sections
        self.accept_formats = accept_formats
        self.update_sequence = update_sequence
        self.constraints = []

    def __call__(self):
        """Process the GetCapabilities request.

        Processing assumes that the relevant parameters have been previously
        set by using the `prepare()` method.

        Returns
        -------
        dict
            A mapping with the capabilities of the requested service.
        int
            The HTTP status code of the operation

        """

        service_to_use = self.get_service_to_use()
        if service_to_use is self.service:
            latest = self.__class__.update_sequence.allowed_values[-1]
            result = {
                "version": self.service.version,
                "updateSequence": latest,
            }
            if self.update_sequence < latest:  # return full capabilities
                logger.info("Preparing full capabilities...")
                sections_info = self.get_sections()
                result.update(sections_info)
            elif self.update_sequence == latest:
                logger.info("Partial capabilities requested")
                pass  # result is complete, no need to add anything else
            else:
                raise CswError(code=INVALID_UPDATE_SEQUENCE)
        elif service_to_use is not None:
            # if the GetCapabilities operation of the service_to_use
            # is enabled, process it and return the result
            try:
                other_op = service_to_use.get_enabled_operation(self.name)
            except PycswError:
                raise CswError(code=VERSION_NEGOTIATION_FAILED)
            else:
                logger.debug("Transferring operation {0.name} to "
                             "service {1}...".format(self, service_to_use))
                result = other_op(
                    accept_versions=self.accept_versions,
                    sections=self.sections,
                    accept_formats=self.accept_formats,
                    update_sequence=self.update_sequence
                )
        else:
            raise CswError(code=VERSION_NEGOTIATION_FAILED)
        return result, 200

    def update_parameter_defaults(self, accept_versions=None, sections=None,
                                  accept_formats=None, update_sequence=None):
        """Update the default values of the operation's parameters.

        This method is called by the pycsw server at the end of its
        initialization. After having been initialized the server can now
        gather details on other available services, which are needed for the
        GetCapabilities operation.

        Parameters
        ----------
        accept_versions: list
            An iterable with strings carrying the default values for  the
            `accept_versions` parameter.
        sections: list
            An iterable with strings carrying the default values for  the
            `sections` parameter.
        accept_formats: list
            An iterable with strings carrying the default values for  the
            `accept_formats` parameter.
        update_sequence: int
            The default value for the `update_sequence` parameter.

        """

        if accept_versions is not None:
            self.__class__.accept_versions.default = list(accept_versions)
        if sections is not None:
            self.__class__.sections.default = list(sections)
        if accept_formats is not None:
            self.__class__.accept_formats.default = list(accept_formats)
        if update_sequence is not None:
            self.__class__.update_sequence.default = update_sequence

    def update_parameter_allowed_values(self, accept_versions=None,
                                        sections=None, accept_formats=None,
                                        update_sequence=None):
        """Update the allowed values values of the operation's parameters.

        This method is called by the pycsw server at the end of its
        initialization. After having been initialized the server can now
        gather details on other available services, which are needed for the
        GetCapabilities operation.

        Parameters
        ----------
        accept_versions: list
            An iterable with strings carrying the allowed values for  the
            `accept_versions` parameter.
        sections: list
            An iterable with strings carrying the allowed values for  the
            `sections` parameter.
        accept_formats: list
            An iterable with strings carrying the allowed values for  the
            `accept_formats` parameter.
        update_sequence: list
            An iterable with ints carrying the allowed values for  the
            `update_sequence` parameter.

        """

        if accept_versions is not None:
            self.__class__.accept_versions.allowed_values = accept_versions
        if sections is not None:
            self.__class__.sections.allowed_values = sections
        if accept_formats is not None:
            self.__class__.accept_formats.allowed_values = accept_formats
        if update_sequence is not None:
            self.__class__.update_sequence.allowed_values = update_sequence

    def prepare(self, accept_versions=None, sections=None,
                accept_formats=None, update_sequence=None):
        try:
            self.accept_versions = accept_versions
        except ValueError:
            raise CswError(code=VERSION_NEGOTIATION_FAILED)

        try:
            self.sections = sections
        except ValueError:
            raise CswError(code=INVALID_PARAMETER_VALUE, locator="sections")
        try:
            self.accept_formats = accept_formats
        except ValueError:
            raise CswError(code=INVALID_PARAMETER_VALUE,
                           locator="accept_formats")
        try:
            self.update_sequence = update_sequence
        except ValueError:
            raise CswError(code=INVALID_UPDATE_SEQUENCE)

    def get_service_to_use(self):
        """Select the service more suitable for servicing the request.

        This method will compare the currently available CSW services on the
        server with the value of the AcceptVersions parameter and select
        the service that is more suitable for processing the request.

        If an appropriate service cannot be found, the server's default CSW
        service is chosen.

        Returns
        -------
        pycsw.services.csw.cswbase.CswService
            The selected service

        """

        for requested in self.accept_versions:
            service = self.service.server.get_service(
                self.service.name, requested)
            if service is not None:
                break
        else:
            service = self.service.server.default_csw_service
        return service

    def get_sections(self):
        """Return information on available capabilities sections."""
        result = {}
        section_getters = {
            "ServiceIdentification": self.get_service_identification,
            "ServiceProvider": self.get_service_provider,
            "OperationsMetadata": self.get_operations_metadata,
            "Contents": self.get_contents,
            "Filter_Capabilities": self.get_filter_capabilities,
        }
        if "All" in self.sections:
            sections = section_getters.keys()
        else:
            sections = self.sections
        for name, getter in section_getters.items():
            allowed = name in self.__class__.sections.allowed_values
            requested = name in sections
            if allowed and requested:
                result[name] = getter()
        return result


    def get_service_identification(self):
        csw_versions = []
        for csw_service in (s for s in self.service.server.services if
                            s.name == "CSW"):
            try:
                csw_service.get_enabled_operation(self.name)
                csw_versions.append(csw_service.version)
            except PycswError:  # GetCapabilities operation is not enabled
                pass

        return {
            "ServiceType": self.service.name,
            "ServiceTypeVersion": csw_versions,
            "Title": self.service.title,
            "Abstract": self.service.abstract,
            "Keywords": self.service.keywords,
            "Fees": self.service.fees,
            "AccessConstraints": self.service.access_constraints,
        }

    def get_service_provider(self):
        provider_contact = self.service.server.provider_contact
        provider_site = self.service.server.provider_site
        contact = provider_contact.contact_info
        return {
            "ProviderName": self.service.server.provider_name,
            "ProviderSite": {
                "linkage": provider_site.linkage,
                "name": provider_site.name,
                "protocol": provider_site.protocol,
                "description": provider_site.description,
            },
            "ServiceContact": {
                "IndividualName": provider_contact.individual_name,
                "PositionName": provider_contact.position_name,
                "Role": provider_contact.role.name,
                "ContactInfo": {
                    "Address": {
                        "AdministrativeArea":
                            contact.address.administrative_area,
                        "City": contact.address.city,
                        "Country": contact.address.country,
                        "DeliveryPoint": contact.address.delivery_point,
                        "ElectronicMailAddress":
                            contact.address.electronic_mail_address,
                        "PostalCode": contact.address.postal_code,
                    },
                    "ContactInstructions": contact.contact_instructions,
                    "HoursOfService": contact.hours_of_service,
                    "OnlineResource": contact.online_resource.linkage,
                    "Phone": contact.phone.voice
                },
                "organisationName": provider_contact.organisation_name,
            }
        }

    # TODO: Generate URLS for DCP metadata
    def get_operations_metadata(self):
        ops = []
        for op in self.service.operations:
            if op.enabled:
                op_data = {
                    "name": op.name,
                    "DCP": [(url[1], url[2]) for url in
                            self.service.get_urls() if url[0] == self],
                    "Parameter": [(p.public_name, p.allowed_values,
                                   p.metadata) for p in op.parameters],
                    "Constraint": [(c.name, c.allowed_values, c.metadata)
                                   for c in op.constraints],
                    "Metadata": [],
                }
                ops.append(op_data)
        return ops

    def get_filter_capabilities(self):
        pass

    def get_contents(self):
        pass
