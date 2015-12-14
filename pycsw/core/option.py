"""Options for pycsw configuration"""

import logging
import datetime

from .etree import etree

logger = logging.getLogger(__name__)


class PycswOption(object):
    name = ""
    default = None
    section = None
    config_parser_name = None

    def __init__(self, name, default=None, section=None,
                 config_parser_name=None, capabilities_name=None,
                 capabilities_namespace=None):
        """Base class for all pycsw options

        :arg name:
        :type name: basestring
        :arg default:
        :type default: anything
        :arg section:
        :type section: basestring
        :arg config_parser_name:
        :type config_parser_name: basestring
        """

        self.name = name
        self.default = default
        self.section = section
        self.config_parser_name = config_parser_name or name
        self.capabilities_name = capabilities_name
        self.capabilities_namespace = capabilities_namespace

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.get(self.section, name)

    def from_dict(self, dict):
        return dict.get(self.name, self.default)

    def to_xml(self, pycsw_server):
        raise NotImplementedError


class StringOption(PycswOption):

    def to_xml(self, pycsw_server):
        element_name = "{{{}}}{}".format(
            pycsw_server.namespaces[self.capabilities_namespace],
            self.capabilities_name
        )
        element = etree.Element(element_name, nsmap=pycsw_server.namespaces)
        element.text = getattr(pycsw_server, self.name)
        return element


class IntegerOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.getint(self.section, name)


class BooleanOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.getboolean(self.section, name)


class StringListOption(PycswOption):

    def __init__(self, capabilities_item_name=None,
                 capabilities_item_namespace=None, *args, **kwargs):
        super(StringListOption, self).__init__(*args, **kwargs)
        self.capabilities_item_name = capabilities_item_name
        self.capabilities_item_namespace = capabilities_item_namespace

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        raw_value = config_parser.get(self.section, name)
        return [item.strip() for item in raw_value.split(",")]

    def to_xml(self, pycsw_server):
        element_name = "{{{}}}{}".format(
            pycsw_server.namespaces[self.capabilities_namespace],
            self.capabilities_name
        )
        element = etree.Element(element_name, nsmap=pycsw_server.namespaces)
        values = getattr(pycsw_server, self.name)
        for value in values:
            sub_element_name = "{{{}}}{}".format(
                pycsw_server.namespaces[self.capabilities_item_namespace],
                self.capabilities_item_name
            )
            sub_element = etree.SubElement(element, sub_element_name,
                                           nsmap=pycsw_server.namespaces)
        return element


class DatetimeOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        raw_value = config_parser.get(self.section, name)
        try:
            the_date_time = datetime.datetime.strptime(raw_value, "%Y-%m-%d")
        except ValueError:
            the_date_time = datetime.datetime.utcnow()
        return the_date_time


class DatetimeListOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        begin, end = config_parser.get(self.section, name).split("/")
        try:
            begin_date_time = datetime.datetime.strptime(begin, "%Y-%m-%d")
            end_date_time = datetime.datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            begin_date_time = datetime.datetime.utcnow()
            end_date_time = datetime.datetime.utcnow()
        return (begin_date_time, end_date_time)


class LoggingOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return getattr(logging, name.upper())


pycsw_options = [
    StringOption("csw_root_path", default="/var/www/pycsw", section="server",
                 config_parser_name="home"),
    StringOption("server_url", default="http://localhost/pycsw/csw.py",
                section="server", config_parser_name="url"),
    StringOption("mimetype", default="application/xml; charset=UTF-8",
                section="server"),
    StringOption("encoding", default="UTF-8", section="server"),
    StringOption("language", default="en-US", section="server"),
    IntegerOption("max_records", default=10, section="server",
                  config_parser_name="maxrecords"),
    LoggingOption("log_level", default=logging.DEBUG, section="server"),
    StringOption("log_file", default="/tmp/pycsw.log", section="server"),
    StringOption("ogc_schemas_base", default="http://foo", section="server"),
    StringListOption("federated_catalogues",
                     default=["http://catalog.data.gov/csw"],
                     section="server"),
    BooleanOption("pretty_print", default=True, section="server"),
    IntegerOption("gzip_compress_level", default=8, section="server"),
    StringOption("domain_query_type", default="range", section="server"),
    BooleanOption("domain_counts", default=True, section="server"),
    BooleanOption("spatial_ranking", default=True, section="server"),
    StringListOption("profiles", default=["apiso"], section="server"),
    BooleanOption("transactions_enabled", default=True, section="manager",
                  config_parser_name="transactions"),
    StringListOption("allowed_ips", default=["127.0.0.1"], section="manager"),
    IntegerOption("csw_harvest_page_size", default=10, section="manager",
                  config_parser_name="harvest_pagesize"),
    StringOption("identification_title", default="pycsw Geospatial Catalogue",
                 section="metadata:main", capabilities_name="Title",
                 capabilities_namespace="ows"),
    StringOption(
        "identification_abstract",
        default="pycsw is an OGC CSW server implementation written in Python",
        section="metadata:main", capabilities_name="Abstract",
        capabilities_namespace="ows"
    ),
    StringListOption("identification_keywords",
                     default=["catalogue", "discovery", "metadata"],
                     section="metadata:main", capabilities_name="Keywords",
                     capabilities_namespace="ows",
                     capabilities_item_name="Keyword",
                     capabilities_item_namespace="ows"),
    StringOption("identification_keywords_type", default="theme",
                 section="metadata:main"),
    StringOption("identification_fees", default="None", section="metadata:main"),
    StringOption("identification_access_constraints", default="None",
                 section="metadata:main",
                 config_parser_name="identification_accessconstraints"),
    StringOption("provider_name", default="Organization Name",
                 section="metadata:main"),
    StringOption("provider_url", default="http://pycsw.org/",
                 section="metadata:main"),
    StringOption("contact_name", default="Lastname, Firstname",
                 section="metadata:main"),
    StringOption("contact_position", default="Position Title",
                 section="metadata:main"),
    StringOption("contact_address", default="Mailing Address",
                 section="metadata:main"),
    StringOption("contact_city", default="City", section="metadata:main"),
    StringOption("contact_state_or_province", default="Administrative Area",
                 section="metadata:main",
                 config_parser_name="contact_stateorprovince"),
    StringOption("contact_postal_code", default="Zip or Postal Code",
                 section="metadata:main",
                 config_parser_name="contact_postalcode"),
    StringOption("contact_country", default="Country",
                 section="metadata:main"),
    StringOption("contact_phone", default="+xx-xxx-xxx-xxxx",
                 section="metadata:main"),
    StringOption("contact_fax", default="+xx-xxx-xxx-xxxx",
                 section="metadata:main"),
    StringOption("contact_email", default="Email Address",
                 section="metadata:main"),
    StringOption("contact_url", default="Contact URL",
                 section="metadata:main"),
    StringOption("contact_hours", default="Hours of Service",
                 section="metadata:main"),
    StringOption("contact_instructions",
                 default="During hours of service. Off on weekends",
                 section="metadata:main"),
    StringOption("contact_role", default="pointOfContact",
                 section="metadata:main"),
    StringOption(
        "database",
        default="sqlite:////var/www/pycsw/tests/suites/cite/data/cite.db",
        #default="postgresql://username:password@localhost/pycsw",
        #default="mysql://username:password@localhost/pycsw?charset=utf8",
        section="repository"
    ),
    StringOption("mappings", default="pycsw.core.mappings",
                 section="repository"),
    StringOption("table", default="records", section="repository"),
    StringOption("filter", default="type='http://purl.org/dcmitype/Dataset'",
                 section="repository"),
    StringOption("source", default="pycsw", section="repository"),
    BooleanOption("inspire_enabled", default=True, section="metadata:inspire",
                  config_parser_name="enabled"),
    StringListOption("inspire_languages_supported", default=["eng", "gre"],
                     section="metadata:inspire",
                     config_parser_name="languages_supported"),
    StringOption("inspire_default_language", default="eng",
                 section="metadata:inspire",
                 config_parser_name="default_language"),
    DatetimeOption("inspire_date", default=datetime.datetime.utcnow(),
                   section="metadata:inspire", config_parser_name="date"),
    StringListOption("inspire_gemet_keywords",
                     default=["Utility and governmental services"],
                     section="metadata:inspire",
                     config_parser_name="gemet_keywords"),
    StringOption("inspire_conformity_service", default="notEvaluated",
                 section="metadata:inspire",
                 config_parser_name="conformity_service"),
    StringOption("inspire_contact_name", default="Organization Name",
                 section="metadata:inspire",
                 config_parser_name="contact_name"),
    StringOption("inspire_contact_email", default="Email Address",
                 section="metadata:inspire",
                 config_parser_name="contact_email"),
    DatetimeListOption("inspire_temp_extent",
                       default=(datetime.datetime.utcnow(),
                                datetime.datetime.utcnow()),
                       section="metadata:inspire",
                       config_parser_name="temp_extent"),
]
