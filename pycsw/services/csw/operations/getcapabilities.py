import logging

from .... import parameters
from ....exceptions import CswError
from ....exceptions import INVALID_UPDATE_SEQUENCE
from ....exceptions import VERSION_NEGOTIATION_FAILED
from ....httprequest import HttpVerb
from ....operationbase import Operation

logger = logging.getLogger(__name__)


# FIXME - It is kind of lame that section names appear on two different places
class GetCapabilities(Operation):
    """GetCapabilities operation.

    Note:
    This class models the GetCapabilities as specified in CSW v2.0.2. There
    are modifications in the OWS standard that most likely apply to CSW v3.0.0.
    therefore this class has to be changed when used in the version 3.0.0

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
        optional=True,
        # similarly to the GetDomain operation, use __init__ to get the
        # allowed values
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
            "Filter_Capabilities",
        ]
    )
    accept_formats = parameters.TextListParameter(
        "AcceptFormats",
        optional=True,
        default="text/xml",  # as defined in OGC 05-008 OWS Common, Table 2
        # allowed values should be calculated from the available
        # ResponseRenderer objects of the service
    )
    update_sequence = parameters.IntParameter(
        "updateSequence",
        optional=True,
        allowed_values=[0, 1],
        default=0
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # OGC CSWv2.0.2 mandates that GetCapabilities
        # must accept GET requests
        self.allowed_http_verbs.add(HttpVerb.GET)
        self._update_accept_formats()
        self._update_accept_versions()

    def __call__(self):
        """Process the GetCapabilities request.

        Processing assumes that the relevant parameters have been previously
        set by using the `set_parameter_values()` method.

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
                # result is complete, no need to add anything else
                logger.info("Partial capabilities requested")
            else:
                raise CswError(code=INVALID_UPDATE_SEQUENCE)
        elif service_to_use is not None:
            # if the GetCapabilities operation of the service_to_use
            # is enabled, process it and return the result
            try:
                other_op = [op for op in service_to_use.operations if
                            op.name == self.name][0]
            except IndexError:
                raise CswError(code=VERSION_NEGOTIATION_FAILED)
            else:
                result = self._execute_another_version(other_op)
        else:
            raise CswError(code=VERSION_NEGOTIATION_FAILED)
        return result, 200

    def get_service_to_use(self):
        """Select the CSW service more suitable for servicing the request.

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

        service = None
        for version in self.accept_versions:
            for existing in self.service.server.services:
                if (existing.name == self.service.name and
                            existing.version == version):
                    service = existing
                    break
            if service is not None:
                break
        else:
            service = self.service.server.get_default_service(
                self.service.name)
        return service

    def get_sections(self):
        """Return information on available capabilities sections.

        This method uses the instance's `sections` attribute in order to know
        what sections have been requested by the client. Therefore, it should
        be preceeded by a call to `update_parameter_values`

        Returns
        -------
        dict
            The information on selected sections.

        """

        result = {}
        getters = {
            "ServiceIdentification": self.get_service_identification,
            "ServiceProvider": self.get_service_provider,
            "OperationsMetadata": self.get_operations_metadata,
            "Contents": self.get_contents,
            "Filter_Capabilities": self.get_filter_capabilities,
        }
        sections = getters.keys() if "All" in self.sections else self.sections
        for section in sections:
            result[section] = getters[section]()
        return result

    def get_service_identification(self):
        """Return information on the service.

        Returns
        -------
        dict
            Metadata information on the service

        """

        if self.service is not None:
            result = {
                "ServiceType": self.service.name,
                "Title": self.service.title,
                "Abstract": self.service.abstract,
                "Keywords": self.service.keywords,
                "Fees": self.service.fees,
                "AccessConstraints": self.service.access_constraints,
            }
            try:
                csw_versions = []
                for csw_service in (s for s in self.service.server.services if
                                    s.name == "CSW"):
                    if self.name in (op.name for op in csw_service.operations):
                        csw_versions.append(csw_service.version)
                result["ServiceTypeVersion"] = csw_versions
            except ValueError:
                pass
        else:
            result = {}
        return result

    def get_service_provider(self):
        """Return metadata information on the service provider."""
        try:
            provider_contact = self.service.server.provider_contact
            provider_site = self.service.server.provider_site
        except ValueError:
            result = {}
        else:
            contact = provider_contact.contact_info
            result = {
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
        return result

    def get_operations_metadata(self):
        return {
            "operations": self._get_service_operations_metadata(),
            "parameters": self._get_service_parameters_metadata(),
            "constraints": self._get_service_constraints_metadata(),
        }

    def get_filter_capabilities(self):
        pass

    def get_contents(self):
        pass

    def _execute_another_version(self, other_operation):
        """Execute another version of the operation.

        This method is used when the client elects a version of the CSW service
        that is different than the current one.

        """

        logger.debug("Transferring operation {0.name} to "
                     "service {1}...".format(self, service_to_use))
        other_operation.accept_versions = self.accept_versions
        other_operation.accept_formats = self.accept_formats
        other_operation.sections = self.sections
        other_operation.update_sequence = self.update_sequence
        return other_operation()

    def _get_service_constraints_metadata(self):
        """Return service constraints

        According to the CSW standard, if the service supports SOAP encoding,
        then there should be a constraint called PostEncoding with the value
        'SOAP' in addition to the value 'XML' (and 'JSON', if supported). This
        means that we must scan available RequestParser objects for the
        server and figure out if these parsers support such POST encodings

        """

        return []  # not properly implemented yet

    def _get_service_parameters_metadata(self):
        return []  # not properly implemented yet

    # TODO: Generate URLS for DCP metadata
    def _get_service_operations_metadata(self):
        result = []
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
                result.append(op_data)
        return result

    def _update_accept_formats(self):
        """Update the accept_formats parameter with available values.

        The service is able to output responses in the formats that are
        available in its ResponseRenderer objects. Therefore we need to scan
        the available renderers and get their output media types.

        """

        available_formats = []
        if self.service is not None:
            for renderer in self.service.response_renderers:
                available_formats.append(renderer.media_type)
            self.__class__.accept_formats.allowed_values = available_formats
            self.accept_formats = available_formats

    def _update_accept_versions(self):
        """Update the accept_versions parameter with the available versions."""

        versions_available = []
        if self.service is not None:
            for service in self.service.server.services:
                versions_available.append(service.version)
            self.__class__.accept_versions.allowed_values = versions_available
            self.accept_versions = versions_available

