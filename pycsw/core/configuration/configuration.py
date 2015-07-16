import os.path
import json
from ConfigParser import SafeConfigParser
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ... import __version__
from . import contextmodels
from .mdcoremodel import MdCoreModel
from ..repositories.base import get_repository


Session = sessionmaker()
LOGGER = logging.getLogger(__name__)


class Context(object):
    repository = None
    md_core_model = MdCoreModel(
        typename="pycsw:CoreMetadata",
        outputschema="http://pycsw.org/metadata",
        mappings_path=os.path.join(os.path.dirname(__file__),
                                   "mappings.json")
    )
    version = __version__
    ogc_schemas_base = 'http://schemas.opengis.net'
    model = None
    loglevel = logging.ERROR
    csw_models = {
        '2.0.2': contextmodels.CswContextModel(),
        '3.0.0': contextmodels.Csw3ContextModel(),
    }
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'csw': 'http://www.opengis.net/cat/csw/2.0.2',
        'csw30': 'http://www.opengis.net/cat/csw/3.0',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dct': 'http://purl.org/dc/terms/',
        'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
        'fes20': 'http://www.opengis.net/fes/2.0',
        'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
        'gmd': 'http://www.isotc211.org/2005/gmd',
        'gmi': 'http://www.isotc211.org/2005/gmi',
        'gml': 'http://www.opengis.net/gml',
        'ogc': 'http://www.opengis.net/ogc',
        'os': 'http://a9.com/-/spec/opensearch/1.1/',
        'ows': 'http://www.opengis.net/ows',
        'ows11': 'http://www.opengis.net/ows/1.1',
        'ows20': 'http://www.opengis.net/ows/2.0',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'soapenv': 'http://www.w3.org/2003/05/soap-envelope',
        'xlink': 'http://www.w3.org/1999/xlink',
        'xs': 'http://www.w3.org/2001/XMLSchema',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    settings = {
        "server": {
            "home": "/var/www/pycsw",
            "url": "http://localhost/pycsw/csw.py",
            "mimetype": "application/xml; charset=UTF-8",
            "encoding": "UTF-8",
            "language": "en-US",
            "maxrecords": 10,
            "logfile": "/tmp/pycsw.log",
            "federatedcatalogues": "http://catalog.data.gov/csw",
            "pretty_print": True,
            "gzip_compresslevel": 8,
            "domainquerytype": "range",
            "domaincounts": True,
            "spatial_ranking": True,
            "profiles": ["apiso",],
        },
        "manager": {
            "transactions": False,
            "allowed_ips": ["127.0.0.1",],
            "csw_harvest_pagesize": 10,
        },
        "metadata:main": {
            "identification_title": "pycsw Geospatial Catalogue",
            "identification_abstract": ("pycsw is an OGC CSW server "
                                        "implementation written in Python"),
            "identification_keywords": "catalogue,discovery,metadata",
            "identification_keywords_type": "theme",
            "identification_fees": "None",
            "identification_accessconstraints": "None",
            "provider_name": "Organization Name",
            "provider_url": "http://pycsw.org/",
            "contact_name": "Lastname, Firstname",
            "contact_position": "Position Title",
            "contact_address": "Mailing Address",
            "contact_city": "City",
            "contact_stateorprovince": "Administrative Area",
            "contact_postalcode": "Zip or Postal Code",
            "contact_country": "Country",
            "contact_phone": "+xx-xxx-xxx-xxxx",
            "contact_fax": "+xx-xxx-xxx-xxxx",
            "contact_email": "Email Address",
            "contact_url": "Contact URL",
            "contact_hours": "Hours of Service",
            "contact_instructions": "During hours of service.  Off on weekends.",
            "contact_role": "pointOfContact",
        },
        "repository": {
            "filter": "type='http://purl.org.dc/dcmitype/Dataset'"
        },
        "metadata:inspire": {
            "enabled": True,
            "languages_supported": "eng,gre",
            "default_language": "eng",
            "date": "YYYY-MM-DD",
            "gemet_keywords": "Utility and governmental services",
            "conformity_service": "notEvaluated",
            "contact_name": "Organization Name",
            "contact_email": "Email Address",
            "temp_extent": "YYYY-MM-DD/YYYY-MM-DD",
        }
    }
    languages = {
        'en': 'english',
        'fr': 'french',
        'el': 'greek',
    }
    response_codes = {
        'OK': '200 OK',
        'NotFound': '404 Not Found',
        'InvalidValue': '400 Invalid property value',
        'OperationParsingFailed': '400 Bad Request',
        'OperationProcessingFailed': '403 Server Processing Failed',
        'OperationNotSupported': '400 Not Implemented',
        'MissingParameterValue': '400 Bad Request',
        'InvalidParameterValue': '400 Bad Request',
        'VersionNegotiationFailed': '400 Bad Request',
        'InvalidUpdateSequence': '400 Bad Request',
        'OptionNotSupported': '400 Not Implemented',
        'NoApplicableCode': '400 Internal Server Error'
    }

    def __init__(self, settings=None, version="3.0.0"):
        """
        Set the context for pycsw

        :param settings:
        :param version:
        :return:
        """
        self.model = self.csw_models[version]
        if settings:
            self.read_config(settings)
        else:
            self.update_repository("sqlite:///:memory:")

    def read_config(self, config):
        """
        Update instance variables by reading the configuration object

        The configuration object is very flexible and can be one of:

        * a python SafeConfigParser instance
        * a python dict
        * a string with the path to a file that is parseable with ConfigParser
        * a string with the path to a file that is parseable with json
        :param config:
        :return:
        """
        if isinstance(config, SafeConfigParser):
            self._read_config_from_config_parser(config)
        elif isinstance(config, dict):
            self._read_config_from_dict(config)
        elif isinstance(config, basestring):
            if config.endswith(".cfg"):
                self._read_config_from_cfg_file_path(config)
            else:
                self._read_config_from_json_file_path(config)

    def update_md_core_model(self, mappings_path):
        self.md_core_model.read_mappings(mappings_path)

    def update_repository(self, database_url, echo=True):
        engine = create_engine(database_url, echo=echo)
        Session.configure(bind=engine)
        session = Session()
        self.repository = get_repository(engine, session)


    def _parse_config_option(self, option, raw_value):
        """Parse a string option into the appropriate data type

        This method is a convenience to workaround the fact that
        SafeConfigParser expects all options to be stored as strings
        """

        # TODO - Parse options that feature dates
        result = raw_value
        as_list = raw_value.split(",")
        if raw_value.lower() == "false":
            result = False
        elif raw_value.lower() == "true":
            result = True
        elif len(as_list) > 1:
            if option not in ("identification_abstract",
                              "identification_accessconstraints",
                              "provider_name", "contact_name",
                              "contact_position", "contact_address",
                              "contact_hours", "contact_instructions"):
                result = as_list
        return result

    def _read_config_from_config_parser(self, config):
        for section in config.sections():
            for option in config.options(section):
                raw_value = config.get(section, option)
                handled = self._handle_special_option(option, raw_value)
                if not handled:
                    value = self._parse_config_option(option, raw_value)
                    self.settings[section][option] = value

    def _read_config_from_dict(self, config_dict):
        for section, section_options in config_dict.iteritems():
            for name, value in section_options.iteritems():
                handled = self._handle_special_option(name, value)
                if not handled:
                    self.settings[section][name] = value

    def _read_config_from_cfg_file_path(self, path):
        with open(path) as fh:
            config = SafeConfigParser.readfp(fh)
            self._read_config_from_config_parser(config)

    def _read_config_from_json_file_path(self, path):
        with open(path) as fh:
            config = json.load(fh)
            self._read_config_from_dict(config)

    def _handle_special_option(self, option, raw_value):
        handled = True
        if option == "loglevel":
            try:
                self.loglevel = getattr(logging, raw_value.upper())
            except AttributeError as err:
                raise RuntimeError(err)
        if option == "database":
            self.update_repository(raw_value)
        elif option == "table":
            pass  # TODO - Handle remapping the table name
        elif option == "mappings":
            self.update_md_core_model(raw_value)
        else:
            handled = False
        return handled


    def gen_domains(self):
        """Generate parameter domain model"""
        domain = {
            "methods": {
                "get": True,
                "post": True,
            },
            "parameters": {
                "ParameterName": {
                    "values": []
                }
            }
        }
        for operation, op_info in self.model["operations"].iteritems():
            for parameter in op_info["parameters"]:
                d = ".".join((operation, parameter))
                domain["parameters"]["ParameterName"]["values"].append(d)
        return domain

    def refresh_dc(self, mappings):
        """Refresh Dublin Core mappings"""

        LOGGER.debug('refreshing Dublin Core mappings with %s' % str(mappings))

        defaults = {
            'dc:title': 'pycsw:Title',
            'dc:creator': 'pycsw:Creator',
            'dc:subject': 'pycsw:Keywords',
            'dct:abstract': 'pycsw:Abstract',
            'dc:publisher': 'pycsw:Publisher',
            'dc:contributor': 'pycsw:Contributor',
            'dct:modified': 'pycsw:Modified',
            'dc:date': 'pycsw:Date',
            'dc:type': 'pycsw:Type',
            'dc:format': 'pycsw:Format',
            'dc:identifier': 'pycsw:Identifier',
            'dc:source': 'pycsw:Source',
            'dc:language': 'pycsw:Language',
            'dc:relation': 'pycsw:Relation',
            'dc:rights': 'pycsw:AccessConstraints',
            'ows:BoundingBox': 'pycsw:BoundingBox',
            'csw:AnyText': 'pycsw:AnyText',
        }

        for k, val in defaults.iteritems():
            for model, params in self.models.iteritems():
                queryables = params['typenames']['csw:Record']['queryables']
                queryables['SupportedDublinCoreQueryables'][k] = {
                    'dbcol': mappings['mappings'][val]
                }


