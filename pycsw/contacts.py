"""Contact related classes modeled after ISO 19115 (2003)."""

import enum


class CiRoleCode(enum.Enum):
    RESOURCE_PROVIDER = "resourceProvider"
    CUSTODIAN = "custodian"
    OWNER = "owner"
    USER = "user"
    DISTRIBUTOR = "distributor"
    ORIGINATOR = "originator"
    POINT_OF_CONTACT = "pointOfContact"
    PRINCIPAL_INVESTIGATOR = "principalInvestigator"
    PROCESSOR = "processor"
    PUBLISHER = "publisher"
    AUTHOR = "author"


class CiOnlineFunctionCode(enum.Enum):
    DOWNLOAD = "download"
    INFORMATION = "information"
    OFFLINE_ACCESS = "offlineAccess"
    ORDER = "order"
    SEARCH = "search"


class IsoOnlineResource:
    """Provides information about an online resource.

    This class is modelled after the CI_OnlineResource type, as described in
    ISO 19115, 2003.

    """

    linkage = ""
    protocol = None
    application_profile = None
    name = None
    description = None
    function = None

    def __init__(self, linkage, protocol=None, application_profile=None,
                 name=None, description=None,
                 function=CiOnlineFunctionCode.DOWNLOAD):
        self.linkage = linkage
        self.protocol = protocol
        self.application_profile = application_profile
        self.name = name
        self.description = description
        self.function = function

    def __str__(self):
        return "{0.__class__.__name__}(linkage={0.linkage})".format(self)

    def __repr__(self):
        return ("{0.__class__.__name__}(linkage={0.linkage!r}, "
                "protocol={0.protocol!r}, "
                "application_profile={0.application_profile!r}, "
                "name={0.name!r}, description={0.description!r},"
                "function={0.function!r})".format(self))


class IsoResponsibleParty:
    """Provides information about an organisation.

    This class is modelled after the CI_ResponsibleParty type, as described in
    ISO 19115, 2003.

    """

    individual_name = None
    organisation_name = None
    position_name = None
    contact_info = None
    role = ""

    def __init__(self, role=CiRoleCode.POINT_OF_CONTACT,
                 individual_name=None, organisation_name=None,
                 position_name=None, contact_info=None):
        self.role = role
        self.individual_name = individual_name
        self.organisation_name = organisation_name
        self.position_name = position_name
        self.contact_info = (contact_info if contact_info is not None
                             else IsoContact())

    @classmethod
    def from_config(cls, config):
        contact_config = config.get("provider", {}).get("contact", {})
        return cls(
            role=contact_config.get("role", "pointofcontact"),  # use CiRoleCode enum
            individual_name=contact_config.get("name", "Placeholder name"),
            organisation_name=config.get(
                "provider", {}).get("name", "Placeholder name"),
            position_name=contact_config.get("position", "Dummy position"),
            contact_info=IsoContact(
                phone=IsoTelephone(
                    voice=contact_config.get("phone", "Dummy telephone"),
                    facsimile=contact_config.get("fax", ""),
                ),
                address=IsoAddress(
                    delivery_point=contact_config.get("address",
                                              "Dummy street address"),
                    city=contact_config.get("city", "Dummy city"),
                    administrative_area=contact_config.get("state_or_province",
                                                           "dummy admin area"),
                    postal_code=contact_config.get("postal_code",
                                                   "dummy postal code"),
                    country=contact_config.get("country", "dummy country"),
                    electronic_mail_address=contact_config.get("email",
                                                               "dummy e-mail")
                ),
                online_resource=IsoOnlineResource(
                    linkage=contact_config.get("url", "dummy link")
                ),
                hours_of_service=contact_config.get("hours", "dummy hours"),
                contact_instructions=contact_config.get("instructions",
                                                        "dummy instructions")
            )
        )


class IsoTelephone:
    """Provides telephone information.

    This class is modelled after the CI_Telephone type, as described in
    ISO 19115, 2003.

    """

    voice = ""
    facsimile = ""

    def __init__(self, voice="", facsimile=""):
        self.voice = voice
        self.facsimile = facsimile


class IsoContact:
    """Provides contact information.

    This class is modelled after the CI_Contact type, as described in
    ISO 19115, 2003.

    """

    phone = None
    address = None
    online_resource = None
    hours_of_service = ""
    contact_instructions = ""

    def __init__(self, phone=None, address=None, online_resource=None,
                 hours_of_service="", contact_instructions=""):
        self.phone = phone if phone is not None else IsoTelephone()
        self.address = address if address is not None else IsoAddress()
        self.online_resource = (online_resource if
                                online_resource is not None else
                                IsoOnlineResource(linkage=""))
        self.hours_of_service = hours_of_service
        self.contact_instructions = contact_instructions


class IsoAddress:
    """Provides address information.

    This class is modelled after the CI_Address type, as described in
    ISO 19115, 2003.

    """

    delivery_point = ""
    city = ""
    administrative_area = ""
    postal_code = ""
    country = ""
    electronic_mail_address = ""

    def __init__(self, delivery_point="", city="", administrative_area="",
                 postal_code="", country="", electronic_mail_address=""):
        self.delivery_point = delivery_point
        self.city = city
        self.administrative_area = administrative_area
        self.postal_code = postal_code
        self.country = country
        self.electronic_mail_address = electronic_mail_address


