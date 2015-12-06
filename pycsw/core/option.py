"""Options for pycsw configuration"""

import logging
import datetime

logger = logging.getLogger(__name__)


class PycswOption(object):
    name = ""
    default = None
    section = None
    config_parser_name = None

    def __init__(self, name, default=None, section=None,
                 config_parser_name=None):
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
        self.config_parser_name = config_parser_name

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.get(self.section, name)

    def from_dict(self, dict):
        return dict.get(self.name, self.default)


class StringOption(PycswOption):
    pass


class IntegerOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.getint(self.section, name)


class BooleanOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return config_parser.getboolean(self.section, name)


class StringListOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        raw_value = config_parser.get(self.section, name)
        return [item.strip() for item in raw_value.split(",")]


class DatetimeOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        raw_value = config_parser.get(self.section, name)
        return datetime.datetime.strptime(raw_value, "%Y-%m-%d")


class DatetimeListOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        begin, end = config_parser.get(self.section, name).split(",")
        begin_date_time = datetime.datetime.strptime(begin, "%Y-%m-%d")
        end_date_time = datetime.datetime.strptime(end, "%Y-%m-%d")
        return (begin_date_time, end_date_time)


class LoggingOption(PycswOption):

    def from_config_parser(self, config_parser):
        name = self.config_parser_name or self.name
        return getattr(logging, name.upper())


pycsw_options = [
    StringOption("csw_root_path", default="/var/www/pycsw", section="server"),
    StringOption("server_url", default="http://localhost/pycsw/csw.py",
                section="server"),
    StringOption("mimetype", default="application/xml; charset=UTF-8",
                section="server"),
    StringOption("encoding", default="UTF-8", section="server"),
    StringOption("language", default="en-US", section="server"),
    IntegerOption("max_records", default=10, section="server"),
    LoggingOption("log_level", default=logging.DEBUG, section="server"),
    StringOption("log_file", default="/tmp/pycsw.log", section="server"),
    StringOption("ogc_schemas_base", default="http://foo", section="server"),
    StringOption("federated_catalogues",
                 default="http://catalog.data.gov/csw",
                 section="server"),
    BooleanOption("pretty_print", default=True, section="server"),
    IntegerOption("gzip_compress_level", default=8, section="server"),
    StringOption("domain_query_type", default="range", section="server"),
    BooleanOption("domain_counts", default=True, section="server"),
    BooleanOption("spatial_ranking", default=True, section="server"),
    StringListOption("profiles", default=["apiso"], section="server"),
    BooleanOption("transactions", default=True, section="manager"),
    StringListOption("allowed_ips", default=["127.0.0.1"], section="manager"),
    IntegerOption("csw_harvest_page_size", default=10, section="manager"),
    StringOption("identification_title", default="pycsw Geospatial Catalogue",
                section="metadata"),
    StringOption(
        "identification_abstract",
        default="pycsw is an OGC CSW server implementation written in Python",
        section="metadata"
    ),
    StringListOption("identification_keywords",
                     default=["catalogue", "discovery", "metadata"],
                     section="metadata"),
    StringOption("identification_keywords_type", default="theme",
                 section="metadata"),
    StringOption("identification_fees", default="None", section="metadata"),
    StringOption("identification_access_constraints", default="None",
                 section="metadata"),
    StringOption("provider_name", default="Organization Name",
                 section="metadata"),
    StringOption("provider_url", default="http://pycsw.org/",
                 section="metadata"),
    StringOption("contact_name", default="Lastname, Firstname",
                 section="metadata"),
    StringOption("contact_position", default="Position Title",
                 section="metadata"),
    StringOption("contact_address", default="Mailing Address",
                 section="metadata"),
    StringOption("contact_city", default="City", section="metadata"),
    StringOption("contact_state_or_province", default="Administrative Area",
                 section="metadata"),
    StringOption("contact_postal_code", default="Zip or Postal Code",
                 section="metadata"),
    StringOption("contact_country", default="Country", section="metadata"),
    StringOption("contact_phone", default="+xx-xxx-xxx-xxxx",
                 section="metadata"),
    StringOption("contact_fax", default="+xx-xxx-xxx-xxxx",
                 section="metadata"),
    StringOption("contact_email", default="Email Address", section="metadata"),
    StringOption("contact_url", default="Contact URL", section="metadata"),
    StringOption("contact_hours", default="Hours of Service",
                 section="metadata"),
    StringOption("contact_instructions",
                 default="During hours of service. Off on weekends",
                 section="metadata"),
    StringOption("contact_role", default="pointOfContact", section="metadata"),
    StringOption(
        "database",
        default="sqlite:////var/www/pycsw/tests/suites/cite/data/cite.db",
        #default="postgresql://username:password@localhost/pycsw",
        #default="mysql://username:password@localhost/pycsw?charset=utf8",
        section="repository"
    ),
    StringOption("mappings", default="path/to/mappings", section="repository"),
    StringOption("table", default="records", section="repository"),
    StringOption("filter", default="type='http://purl.org/dcmitype/Dataset'",
                 section="repository"),
    StringOption("source", default="pycsw", section="repository"),
    BooleanOption("enabled", default=True, section="metadata:inspire"),
    StringListOption("languages_supported", default=["eng", "gre"],
                     section="metadata:inspire"),
    StringOption("default_language", default="eng",
                 section="metadata:inspire"),
    DatetimeOption("date", default=datetime.datetime.utcnow(),
                   section="metadata:inspire"),
    StringListOption("gemet_keywords",
                     default=["Utility and governmental services"],
                     section="metadata:inspire"),
    StringOption("conformity_service", default="notEvaluated",
                 section="metadata:inspire"),
    StringOption("contact_name", default="Organization Name",
                 section="metadata:inspire"),
    StringOption("contact_email", default="Email Address",
                 section="metadata:inspire"),
    DatetimeListOption("temp_extent",
                       default=(datetime.datetime.utcnow(),
                                datetime.datetime.utcnow()),
                       section="metadata:inspire"),
]
