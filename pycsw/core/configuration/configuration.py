from ConfigParser import SafeConfigParser
import logging

from ... import __version__
from . import contextmodels
from .mdcoremodel import md_core_model


LOGGER = logging.getLogger(__name__)


class NewConfiguration(object):

    version = __version__
    ogc_schemas_base = 'http://schemas.opengis.net'
    home = "/var/www/pycsw"
    url = "http://localhost/pycsw/csw.py"
    mimetype = "application/xml; charset=UTF-8"
    encoding = "UTF-8"
    language = "en-US"
    maxrecords = 10
    loglevel = "DEBUG"
    logfile = "/tmp/pycsw.log"
    federatedcatalogues = "http://catalog.data.gov/csw"
    pretty_print = True
    gzip_compresslevel = 8
    domainquerytype = "range"
    domaincounts = True
    spatial_ranking = True
    profiles = ["apiso",]
    transactions = False
    allowed_ips = ["127.0.0.1",]
    csw_harvest_pagesize = 10
    identification_title = "pycsw Geospatial Catalogue"
    identification_abstract = ("pycsw is an OGC CSW server implementation "
                               "written in Python")
    identification_keywords = "catalogue,discovery,metadata"
    identification_keywords_type = "theme"
    identification_fees = "None"
    identification_accessconstraints = "None"
    provider_name = "Organization Name"
    provider_url = "http://pycsw.org/"
    contact_name = "Lastname, Firstname"
    contact_position = "Position Title"
    contact_address = "Mailing Address"
    contact_city = "City"
    contact_stateorprovince = "Administrative Area"
    contact_postalcode = "Zip or Postal Code"
    contact_country = "Country"
    contact_phone = "+xx-xxx-xxx-xxxx"
    contact_fax = "+xx-xxx-xxx-xxxx"
    contact_email = "Email Address"
    contact_url = "Contact URL"
    contact_hours = "Hours of Service"
    contact_instructions = "During hours of service.  Off on weekends."
    contact_role = "pointOfContact"
    # sqlite
    database = "sqlite:////var/www/pycsw/tests/suites/cite/data/records.db"
    # postgres
    #database = "postgresql://username:password@localhost/pycsw"
    # mysql
    #database = "mysql://username:password@localhost/pycsw?charset=utf8"
    table = "records"
    filter = "type = 'http://purl.org/dc/dcmitype/Dataset'"
    inspire_settings = {
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
    languages = {
        'en': 'english',
        'fr': 'french',
        'el': 'greek',
    }
    model = None
    models = {
        'csw': contextmodels.CswContextModel(),
        'csw30': contextmodels.Csw3ContextModel(),
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
    md_core_model = md_core_model

    def __init__(self, prefix="csw30"):
        self.model = self.models[prefix]

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
            self._read_config_from_file_path(config)

    def _read_config_from_config_parser(self, config):
        pass

    def _read_config_from_dict(self, config_dict):
        for k, v in config_dict.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                LOGGER.warning(
                    "Configuration parameter {} is not recognized".format(k))

    def _read_config_from_cfg_file_path(self, path):
        pass

    def _read_config_from_json_file_path(self, path):
        pass

    def update_mappings(self, new_mappings):
        self.md_core_model["mappings"] = new_mappings
        self.refresh_dc(new_mappings)

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


