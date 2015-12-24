# -*- coding: iso-8859-15 -*-
# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Angelos Tzotsos <tzotsos@gmail.com>
#
# Copyright (c) 2015 Tom Kralidis
# Copyright (c) 2015 Angelos Tzotsos
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

"""Pycsw server.

This module defines the :class:`PycswServer` class, which is the main entry
point for pycsw. A typical workflow is to create a request from the existing
wsgi environment (which is created by the webserver), create a
:class:`PycswServer` instance with the proper configuration parameters, and
then dispatch the request for processing:

.. doctest::

   >>> import os
   >>> import logging
   >>> import wsgiref.util
   >>> from pycsw.core.request import PycswHttpRequest
   >>> from pycsw.server import PycswServer
   >>> # simulate an incoming HTTP request
   >>> environment = {}
   >>> wsgiref.util.setup_testing_defaults(environment)
   >>> request = PycswHttpRequest(**environment)
   >>> # instantiate pycsw server
   >>> server = PycswServer(
   ...     database=os.path.expanduser("~/dev/pycsw/records.db"),
   ...     log_level=logging.INFO
   ... )
   >>> # dispatch the request
   >>> status_code, response, response_headers = server.dispatch(request)
"""

import os
import sys
from time import time
from urllib2 import quote, unquote
import urlparse
from cStringIO import StringIO
import ConfigParser
import logging
import json
import codecs
import importlib
import io

from pycsw.core.etree import etree
from pycsw import oaipmh, opensearch, sru
from pycsw.plugins.profiles import profile as pprofile
import pycsw.plugins.outputschemas
from pycsw.core import config, log, util
from pycsw.ogc.csw import csw2, csw3

from pycsw.core.option import pycsw_options
from pycsw.core.request import PycswHttpRequest
from pycsw.plugins.profiles.profile import Profile

from . import exceptions

LOGGER = logging.getLogger(__name__)


class PycswServer(object):

    accept_versions = [util.CSW_VERSION_2_0_2, util.CSW_VERSION_3_0_0]
    # defaulting to 2.0.2 while 3.0.0 is not out
    csw_version = util.CSW_VERSION_2_0_2
    repository = None
    encoding = sys.getdefaultencoding()
    language = "eng"
    ogc_schemas_base = ""
    log_level = logging.DEBUG
    log_file = None

    def __init__(self, rtconfig=None, reconfigure_logging=True, **kwargs):
        """Pycsw server

        :param rtconfig: One of several possible configuration specifications
        :type rtconfig: str or dict
        :param reconfigure_logging: Whether logging should be reconfigured
            with the log_level and log_file values specified in the
            supplied configuration
        :type reconfigure_logging: bool
        :param kwargs: Extra confguration values can be explicitly passed when
            creating a server object
        :raises:

        Create a new pycsw server that processes incoming requests. When
        instantiated, the server loads its configuration from the input
        arguments. After creation the server is ready to process requests.
        """

        configuration = self.get_configuration(rtconfig, **kwargs)
        if reconfigure_logging:
            util.reconfigure_logging(configuration["log_level"],
                                     configuration["log_file"])
        self.context = config.StaticContext()
        LOGGER.info("loaded context")
        if configuration["transactions_enabled"]:
            self.context.enable_transactions()
            LOGGER.info("enabled transaction support")
        mappings = self.get_mappings(configuration["mappings"])
        self.update_mappings(mappings)
        LOGGER.info("loaded mappings")
        repository, orm = self.get_repository(
            source=configuration["source"],
            database=configuration["database"],
            table=configuration["table"],
            filter_=configuration["filter"]
        )
        self.repository = repository
        LOGGER.info("loaded repository")
        self.orm = orm
        # don't need these configuration parameters anymore
        del configuration["log_level"]
        del configuration["log_file"]
        del configuration["transactions_enabled"]
        del configuration["source"]
        del configuration["database"]
        del configuration["mappings"]
        del configuration["table"]
        del configuration["filter"]
        # generate instance variables from remaining configuration values
        for name, value in configuration.items():
            setattr(self, name, value)
        LOGGER.info("loaded server attributes")
        self.profiles = []
        loaded_profiles = ""
        for profile in self.get_profiles(configuration["profiles"]):
            profile.extend_core(self.context.model,
                                self.context.namespaces,
                                self)
            self.profiles.append(profile)
            loaded_profiles += profile.__class__.__name__
        LOGGER.info("loaded profiles: {}".format(loaded_profiles))
        # generate distributed search model
        # generate domain model

    def dispatch(self, request):
        """Dispatch an incoming request for processing.

        This is the main interaction point for client code. This method parses
        the input request and determines which operation mode is being
        requested. It then delegates processing to the appropriate mode.

        :arg request: The incoming request
        :type request: :class:`~pycsw.core.request.PycswHttpRequest`
        :return:
        :raises:
        """

        requested_mode = request.GET.get("mode",
                                         request.POST.get("mode", "csw"))
        LOGGER.info("dispatching mode {}".format(requested_mode))
        dispatch_method = {
            "csw": self.dispatch_csw,
            "sru": self.dispatch_sru,
            "oaipmh": self.dispatch_oaipmh,
            "opensearch": self.dispatch_opensearch,
        }.get(requested_mode)
        return dispatch_method(request)

    def dispatch_csw(self, request):
        """Dispatch the input CSW request for processing

        :param request: The incoming CSW request
        :type request: :class:`~pycsw.core.request.PycswHttpRequest`
        :return:
        :raise:
        """

        if self._get_requested_service(request) != util.CSW_SERVICE:
            raise exceptions.PycswError(code=exceptions.NO_APPLICABLE_CODE)
        requested_version = self._get_requested_csw_version(request)
        try:
            csw_version_class_info = {
                util.CSW_VERSION_2_0_2: ("pycsw.ogc.csw2", "Csw2"),
                util.CSW_VERSION_3_0_0: ("pycsw.ogc.csw3", "Csw3"),
            }[self._get_requested_csw_version(request)]
        except KeyError:
            raise exceptions.PycswError(exceptions.VERSION_NEGOTIATION_FAILED)
        csw_version_class = util.lazy_import_dependency(
            *csw_version_class_info)
        csw_interface = csw_version_class(self)
        LOGGER.info("Using csw_interface {}".format(csw_interface))
        return csw_interface.dispatch(request)

    def dispatch_sru(self, request):
        """Dispatch the input SRU request for processing

        :param request:
        :type request:
        :return:
        :raise:
        """
        sru_wrapper_class = util.lazy_import_dependency("pycsw.sru", "Sru")
        sru = sru_wrapper_class(self.context)
        query_dict = request.GET.copy()
        query_dict.update(request.POST)
        new_query_dict = sru.request_sru2csw(query_dict)
        new_request = PycswHttpRequest(**request.META)
        new_request.GET = new_query_dict
        new_request.POST = {}
        csw_result = self.dispatch_csw(new_request)
        sru.response_csw2sru()
        raise NotImplementedError

    def dispatch_oaipmh(self, request):
        raise NotImplementedError

    def dispatch_opensearch(self, request):
        raise NotImplementedError

    def get_configuration(self, runtime_settings=None, **kwargs):
        """Load pycsw configuration from multiple input sources

        :param runtime_settings:
        :param kwargs:
        :return:
        :rtype: dict
        """
        # get default options first
        the_config = {opt.name: opt.default for opt in pycsw_options}
        # now try to override with any input configuration sources
        if isinstance(runtime_settings, basestring):
            to_load = self.get_configuration_from_file(runtime_settings)
        elif isinstance(runtime_settings, ConfigParser.SafeConfigParser):
            to_load = self.get_configuration_from_config_parser(
                runtime_settings)
        elif runtime_settings is not None:
            to_load = self.get_configuration_from_dict(runtime_settings)
        else:
            to_load = {opt.name: opt.default for opt in pycsw_options}
        to_load.update(kwargs)
        the_config.update(to_load)
        return the_config

    @classmethod
    def get_configuration_from_config_parser(cls, configuration):
        options_dict = {(opt.section, opt.config_parser_name): opt for
                        opt in pycsw_options}
        to_load = {}
        for section in configuration.sections():
            for name in configuration.options(section):
                try:
                    pycsw_option = options_dict[(section, name)]
                    name = pycsw_option.name
                    parsed_value = pycsw_option.from_config_parser(
                        configuration)
                except KeyError:
                    raise RuntimeError(
                        "Invalid option: {}:{}".format(section, name))
                to_load[name] = parsed_value
        return to_load

    def get_configuration_from_dict(self, configuration):
        # this is just a convenience conversion to make searching for options
        # faster. It is a small nuissance but nicer to the users:
        # pycsw_options can be a list (and easier to define) rather than
        # a dict
        options_dict = {opt.name: opt for opt in pycsw_options}
        to_load = {}
        for key, value in configuration.items():
            try:
                pycsw_option = options_dict[key]
                name = pycsw_option.name
                parsed_value = pycsw_option.from_dict(configuration)
            except KeyError:  # this is some custom option
                name = key
                parsed_value = value
            to_load[name] = parsed_value
        return to_load

    def get_configuration_from_file(self, path):
        parsed = None
        try:
            with io.open(path, encoding=self.encoding) as fh:
                try:
                    config_dict = json.load(fh)
                    parsed = self.get_configuration_from_dict(config_dict)
                except ValueError:
                    # could not decode JSON, maybe its configparser
                    fh.seek(0)  # rewind the file object back to beginning
                    try:
                        config_parser = ConfigParser.SafeConfigParser()
                        config_parser.readfp(fh)
                        parsed = self.get_configuration_from_config_parser(
                            config_parser)
                    except Exception:  # FIXME - replace with proper exception
                        raise PycswError(
                            "", "",
                            "Unable to load configuration file"
                        )
        except IOError:
            raise PycswError("", "",
                             "Unable to open configuration file")
        return parsed

    def get_mappings(self, mappings_path):
        if os.sep in mappings_path:  # its a filesystem path
            module_path = os.path.splitext(mappings_path)[0].replace(
                os.sep, ".")
        else:  # its a python path
            module_path = mappings_path
        LOGGER.debug("Loading custom repository mappings "
                     "from {}".format(module_path))
        try:
            mappings_module = util.lazy_import_dependency(module_path)
        except IOError as err:
            raise PycswError(
                "NoApplicableCode", "service",
                "Could not load repository mappings: {}".format(err))
        return mappings_module

    def get_profiles(self, profile_names):
        profiles = []
        for name in profile_names:
            # try to load it as the profile name
            python_path = "pycsw.plugins.profiles.{0}.{0}".format(name)
            found_profiles = self._probe_for_profiles(python_path)
            if not any(found_profiles):
                # try to load it a a python path
                found_profiles = self._probe_for_profiles(name)
                if not any(found_profiles):
                    # try to load it as a filesystem path
                    python_path = name.replace(os.path.sep, ".")
                    found_profiles = self._probe_for_profiles(python_path)
            profiles.extend(found_profiles)
        return profiles

    def get_repository(self, source="pycsw", database="", mappings="",
                       table="", filter_=""):
        repo_parameters = {
            "geonode": {
                "path": ("pycsw.plugins.repository.geonode.geonode_",
                         "GeoNodeRepository"),
                "args": (self.context, filter_),
            },
            "odc": {
                "path": ("pycsw.plugins.repository.odc",
                         "OpenDataCatalogRepository"),
                "args": (self.context, filter_),
            },
            "pycsw": {
                "path": ("pycsw.core.repository", "Repository"),
                "args": (database, self.context, None,
                         table, filter_),
                "orm": "sqlalchemy",
            },
        }.get(source)
        repo_class = util.lazy_import_dependency(*repo_parameters["path"])
        orm = repo_parameters.get("orm")
        try:
            repository = repo_class(*repo_parameters["args"])
            LOGGER.debug("Repository loaded ({})".format(source))
        except Exception as err:
            raise PycswError(
                "NoApplicableCode",
                "service",
                "Could not load repository ({}): {} - {}".format(
                    source, database, err)
            )
        return repository, orm

    def update_mappings(self, mappings):
        self.context.md_core_model = mappings.MD_CORE_MODEL
        self.context.refresh_dc(mappings.MD_CORE_MODEL)

    def _get_requested_csw_version(self, request):
        version_string = "version"
        version = request.GET.get(version_string,
                                  request.POST.get(version_string))
        if version is None:  # get the version from the body of the request
            re_module = util.lazy_import_dependency("re")
            try:
                version = re_module.search(
                    r'{}="(\d\.\d\.\d)"'.format(version_string),
                    request.body
                ).group(1)
            except AttributeError:
                # FIXME - look up the proper exception values
                raise PycswError(self, None, None, None)
        return version

    def _get_requested_service(self, request):
        service_string = "service"
        service = request.GET.get(service_string,
                                  request.POST.get(service_string))
        if service is None:  # get the service from the body of the request
            re_module = util.lazy_import_dependency("re")
            try:
                service = re_module.search(
                    r'{}="(.*?)"'.format(service_string),
                    request.body
                ).group(1)
            except AttributeError:
                # could not find the requested service name
                # FIXME - look up the proper exception values
                raise PycswError(self, None, None, None)
        return service

    def _probe_for_profiles(self, python_path):
        try:
            python_module = util.lazy_import_dependency(python_path)
        except ImportError as err:
            raise PycswError("", "",
                             "Invalid profile: {}".format(python_path))
        profiles = []
        for obj_type in python_module.__dict__.values():
            try:
                if issubclass(obj_type, Profile):
                    profile_instance = obj_type(self.context.model,
                                                self.context.namespaces,
                                                self.context)
                    profiles.append(profile_instance)
            except TypeError:
                pass  # this obj_type was not a class, ignore it
        return profiles


class Csw(object):
    """ Base CSW server """
    def __init__(self, rtconfig=None, env=None, version='3.0.0'):
        """ Initialize CSW """

        if not env:
            self.environ = os.environ
        else:
            self.environ = env

        self.context = config.StaticContext()

        # Lazy load this when needed
        # (it will permanently update global cfg namespaces)
        self.sruobj = None
        self.opensearchobj = None
        self.oaipmhobj = None

        # init kvp
        self.kvp = {}

        self.mode = 'csw'
        self.async = False
        self.soap = False
        self.request = None
        self.exception = False
        self.status = 'OK'
        self.profiles = None
        self.manager = False
        self.outputschemas = {}
        self.mimetype = 'application/xml; charset=UTF-8'
        self.encoding = 'UTF-8'
        self.pretty_print = 0
        self.domainquerytype = 'list'
        self.orm = 'django'
        self.language = {'639_code': 'en', 'text': 'english'}
        self.process_time_start = time()

        # define CSW implementation object (default CSW3)
        self.iface = csw3.Csw3(server_csw=self)
        self.request_version = version

        if self.request_version == '2.0.2':
            self.iface = csw2.Csw2(server_csw=self)
            self.context.set_model('csw')

        # load user configuration
        try:
            if isinstance(rtconfig, ConfigParser.SafeConfigParser):  # serialized already
                self.config = rtconfig
            else:
                self.config = ConfigParser.SafeConfigParser()
                if isinstance(rtconfig, dict):  # dictionary
                    for section, options in rtconfig.items():
                        self.config.add_section(section)
                        for k, v in options.items():
                            self.config.set(section, k, v)
                else:  # configuration file
                    import codecs
                    with codecs.open(rtconfig, encoding='utf-8') as scp:
                        self.config.readfp(scp)
        except Exception:
            self.response = self.iface.exceptionreport(
                'NoApplicableCode', 'service',
                'Error opening configuration %s' % rtconfig
            )
            return

        # set server.home safely
        # TODO: make this more abstract
        self.config.set(
            'server', 'home',
            os.path.dirname(os.path.join(os.path.dirname(__file__), '..'))
        )

        self.context.pycsw_home = self.config.get('server', 'home')
        self.context.url = self.config.get('server', 'url')

        log.setup_logger(self.config)

        LOGGER.debug('running configuration %s' % rtconfig)
        LOGGER.debug(str(self.environ['QUERY_STRING']))

        # set OGC schemas location
        if not self.config.has_option('server', 'ogc_schemas_base'):
            self.config.set('server', 'ogc_schemas_base',
                            self.context.ogc_schemas_base)

        # set mimetype
        if self.config.has_option('server', 'mimetype'):
            self.mimetype = self.config.get('server', 'mimetype').encode()

        # set encoding
        if self.config.has_option('server', 'encoding'):
            self.encoding = self.config.get('server', 'encoding')

        # set domainquerytype
        if self.config.has_option('server', 'domainquerytype'):
            self.domainquerytype = self.config.get('server', 'domainquerytype')

        # set XML pretty print
        if (self.config.has_option('server', 'pretty_print') and
                self.config.get('server', 'pretty_print') == 'true'):
            self.pretty_print = 1

        # set Spatial Ranking option
        if (self.config.has_option('server', 'spatial_ranking') and
                self.config.get('server', 'spatial_ranking') == 'true'):
            util.ranking_enabled = True

        # set language default
        if self.config.has_option('server', 'language'):
            try:
                LOGGER.info('Setting language')
                lang_code = self.config.get('server', 'language').split('-')[0]
                self.language['639_code'] = lang_code
                self.language['text'] = self.context.languages[lang_code]
            except:
                pass

        LOGGER.debug('Configuration: %s.' % self.config)
        LOGGER.debug('Model: %s.' % self.context.model)

        # load user-defined mappings if they exist
        if self.config.has_option('repository', 'mappings'):
            # override default repository mappings
            try:
                import imp
                module = self.config.get('repository', 'mappings')
                modulename = '%s' % os.path.splitext(module)[0].replace(
                    os.sep, '.')
                LOGGER.debug('Loading custom repository mappings '
                             'from %s.' % module)
                mappings = imp.load_source(modulename, module)
                self.context.md_core_model = mappings.MD_CORE_MODEL
                self.context.refresh_dc(mappings.MD_CORE_MODEL)
            except Exception as err:
                self.response = self.iface.exceptionreport(
                    'NoApplicableCode', 'service',
                    'Could not load repository.mappings %s' % str(err)
                )

        # load outputschemas
        LOGGER.debug('Loading outputschemas.')

        for osch in pycsw.plugins.outputschemas.__all__:
            output_schema_module = __import__(
                'pycsw.plugins.outputschemas.%s' % osch)
            mod = getattr(output_schema_module.plugins.outputschemas, osch)
            self.outputschemas[mod.NAMESPACE] = mod

        LOGGER.debug('Outputschemas loaded: %s.' % self.outputschemas)
        LOGGER.debug('Namespaces: %s' % self.context.namespaces)

    def expand_path(self, path):
        """ return safe path for WSGI environments """
        if 'local.app_root' in self.environ and not os.path.isabs(path):
            return os.path.join(self.environ['local.app_root'], path)
        else:
            return path

    def dispatch_wsgi(self):
        """ WSGI handler """

        if hasattr(self, 'response'):
            return self._write_response()

        LOGGER.debug('WSGI mode detected')

        if self.environ['REQUEST_METHOD'] == 'POST':
            try:
                request_body_size = int(self.environ.get('CONTENT_LENGTH', 0))
            except (ValueError):
                request_body_size = 0

            self.requesttype = 'POST'
            self.request = self.environ['wsgi.input'].read(request_body_size)
            LOGGER.debug('Request type: POST.  Request:\n%s\n', self.request)

        else:  # it's a GET request
            self.requesttype = 'GET'

            scheme = '%s://' % self.environ['wsgi.url_scheme']

            if self.environ.get('HTTP_HOST'):
                url = '%s%s' % (scheme, self.environ['HTTP_HOST'])
            else:
                url = '%s%s' % (scheme, self.environ['SERVER_NAME'])

                if self.environ['wsgi.url_scheme'] == 'https':
                    if self.environ['SERVER_PORT'] != '443':
                        url += ':' + self.environ['SERVER_PORT']
                else:
                    if self.environ['SERVER_PORT'] != '80':
                        url += ':' + self.environ['SERVER_PORT']

            url += quote(self.environ.get('SCRIPT_NAME', ''))
            url += quote(self.environ.get('PATH_INFO', ''))

            if self.environ.get('QUERY_STRING'):
                url += '?' + self.environ['QUERY_STRING']

            self.request = url
            LOGGER.debug('Request type: GET.  Request:\n%s\n', self.request)

            pairs = self.environ.get('QUERY_STRING').split("&")

            kvp = {}

            for pairstr in pairs:
                pair = [unquote(a) for a in pairstr.split("=")]
                kvp[pair[0]] = pair[1] if len(pair) > 1 else ""
            self.kvp = kvp

        return self.dispatch()

    def opensearch(self):
        """ enable OpenSearch """
        if not self.opensearchobj:
            self.opensearchobj = opensearch.OpenSearch(self.context)

        return self.opensearchobj

    def sru(self):
        """ enable SRU """
        if not self.sruobj:
            self.sruobj = sru.Sru(self.context)

        return self.sruobj

    def oaipmh(self):
        """ enable OAI-PMH """
        if not self.oaipmhobj:
            self.oaipmhobj = oaipmh.OAIPMH(self.context, self.config)
        return self.oaipmhobj

    def dispatch(self, writer=sys.stdout, write_headers=True):
        """ Handle incoming HTTP request """

        if self.requesttype == 'GET':
            self.kvp = self.normalize_kvp(self.kvp)
            version_202 = ('version' in self.kvp and
                           self.kvp['version'] == '2.0.2')
            accept_version_202 = ('acceptversions' in self.kvp and
                                  '2.0.2' in self.kvp['acceptversions'])
            if version_202 or accept_version_202:
                self.request_version = '2.0.2'
        elif self.requesttype == 'POST':
            if self.request.find('2.0.2') != -1:
                self.request_version = '2.0.2'

        if (not isinstance(self.kvp, str) and 'mode' in self.kvp and
                self.kvp['mode'] == 'sru'):
            self.mode = 'sru'
            self.request_version = '2.0.2'
            LOGGER.debug('SRU mode detected; processing request.')
            self.kvp = self.sru().request_sru2csw(self.kvp)

        if (not isinstance(self.kvp, str) and 'mode' in self.kvp and
                self.kvp['mode'] == 'oaipmh'):
            self.mode = 'oaipmh'
            self.request_version = '2.0.2'
            LOGGER.debug('OAI-PMH mode detected; processing request.')
            self.oaiargs = dict((k, v) for k, v in self.kvp.items() if k)
            self.kvp = self.oaipmh().request(self.kvp)

        if self.request_version == '2.0.2':
            self.iface = csw2.Csw2(server_csw=self)
            self.context.set_model('csw')

        # configure transaction support, if specified in config
        self._gen_manager()

        namespaces = self.context.namespaces
        ops = self.context.model['operations']
        constraints = self.context.model['constraints']
        # generate domain model
        # NOTE: We should probably avoid this sort of mutable state for WSGI
        if 'GetDomain' not in ops:
            ops['GetDomain'] = self.context.gen_domains()

        # generate distributed search model, if specified in config
        if self.config.has_option('server', 'federatedcatalogues'):
            LOGGER.debug('Configuring distributed search.')
            constraints['FederatedCatalogues'] = {'values': []}

            for fedcat in self.config.get('server',
                                          'federatedcatalogues').split(','):
                constraints['FederatedCatalogues']['values'].append(fedcat)

        for key, value in self.outputschemas.items():
            get_records_params = ops['GetRecords']['parameters']
            get_records_params['outputSchema']['values'].append(
                value.NAMESPACE)
            get_records_by_id_params = ops['GetRecordById']['parameters']
            get_records_by_id_params['outputSchema']['values'].append(
                value.NAMESPACE)
            if 'Harvest' in ops:
                harvest_params = ops['Harvest']['parameters']
                harvest_params['ResourceType']['values'].append(
                    value.NAMESPACE)

        LOGGER.debug('Setting MaxRecordDefault')
        if self.config.has_option('server', 'maxrecords'):
            constraints['MaxRecordDefault']['values'] = [
                self.config.get('server', 'maxrecords')]

        # load profiles
        if self.config.has_option('server', 'profiles'):
            self.profiles = pprofile.load_profiles(
                os.path.join('pycsw', 'plugins', 'profiles'),
                pprofile.Profile,
                self.config.get('server', 'profiles')
            )

            for prof in self.profiles['plugins'].keys():
                tmp = self.profiles['plugins'][prof](self.context.model,
                                                     namespaces,
                                                     self.context)

                key = tmp.outputschema  # to ref by outputschema
                self.profiles['loaded'][key] = tmp
                self.profiles['loaded'][key].extend_core(self.context.model,
                                                         namespaces,
                                                         self.config)

            LOGGER.debug(
                'Profiles loaded: %s.' % self.profiles['loaded'].keys())

        # init repository
        # look for tablename, set 'records' as default
        if not self.config.has_option('repository', 'table'):
            self.config.set('repository', 'table', 'records')

        repo_filter = None
        if self.config.has_option('repository', 'filter'):
            repo_filter = self.config.get('repository', 'filter')

        if (self.config.has_option('repository', 'source') and
                self.config.get('repository', 'source') == 'geonode'):

            # load geonode repository
            from pycsw.plugins.repository.geonode import geonode_

            try:
                self.repository = geonode_.GeoNodeRepository(self.context,
                                                             repo_filter)
                LOGGER.debug('GeoNode repository loaded '
                             '(geonode): %s.' % self.repository.dbtype)
            except Exception as err:
                self.response = self.iface.exceptionreport(
                    'NoApplicableCode', 'service',
                    'Could not load repository (geonode): %s' % str(err)
                )

        elif (self.config.has_option('repository', 'source') and
                self.config.get('repository', 'source') == 'odc'):

            # load odc repository
            from pycsw.plugins.repository.odc import odc

            try:
                self.repository = odc.OpenDataCatalogRepository(self.context,
                                                                repo_filter)
                LOGGER.debug('OpenDataCatalog repository loaded '
                             '(geonode): %s.' % self.repository.dbtype)
            except Exception as err:
                self.response = self.iface.exceptionreport(
                    'NoApplicableCode', 'service',
                    'Could not load repository (odc): %s' % str(err)
                )

        else:  # load default repository
            self.orm = 'sqlalchemy'
            from pycsw.core import repository
            try:
                self.repository = repository.Repository(
                    self.config.get('repository', 'database'),
                    self.context,
                    self.environ.get('local.app_root', None),
                    self.config.get('repository', 'table'),
                    repo_filter
                )
                LOGGER.debug(
                    'Repository loaded (local): %s.' % self.repository.dbtype)
            except Exception as err:
                self.response = self.iface.exceptionreport(
                    'NoApplicableCode', 'service',
                    'Could not load repository (local): %s' % str(err)
                )

        if self.requesttype == 'POST':
            LOGGER.debug(self.iface.version)
            self.kvp = self.iface.parse_postdata(self.request)

        error = 0

        if isinstance(self.kvp, str):  # it's an exception
            error = 1
            locator = 'service'
            text = self.kvp
            if (self.kvp.find('the document is not valid') != -1 or
                    self.kvp.find('document not well-formed') != -1):
                code = 'NoApplicableCode'
            else:
                code = 'InvalidParameterValue'

        LOGGER.debug('HTTP Headers:\n%s.' % self.environ)
        LOGGER.debug('Parsed request parameters: %s' % self.kvp)

        if (not isinstance(self.kvp, str) and 'mode' in self.kvp and
                self.kvp['mode'] == 'opensearch'):
            self.mode = 'opensearch'
            LOGGER.debug('OpenSearch mode detected; processing request.')
            self.kvp['outputschema'] = 'http://www.w3.org/2005/Atom'

        if ((self.kvp == {'': ''} and self.request_version == '3.0.0') or
                (len(self.kvp) == 1 and 'config' in self.kvp)):
            LOGGER.debug('Turning on default csw30:Capabilities for base URL')
            self.kvp = {
                'service': 'CSW',
                'acceptversions': '3.0.0',
                'request': 'GetCapabilities'
            }
            http_accept = self.environ.get('HTTP_ACCEPT', '')
            if 'application/opensearchdescription+xml' in http_accept:
                self.mode = 'opensearch'
                self.kvp['outputschema'] = 'http://www.w3.org/2005/Atom'

        if error == 0:
            # test for the basic keyword values (service, version, request)
            basic_options = ['service', 'request']
            request = self.kvp.get('request', '')
            own_version_integer = util.get_version_integer(
                self.request_version)
            if self.request_version == '2.0.2':
                basic_options.append('version')

            for k in basic_options:
                if k not in self.kvp:
                    if (k in ['version', 'acceptversions'] and
                            request == 'GetCapabilities'):
                        pass
                    else:
                        error = 1
                        locator = k
                        code = 'MissingParameterValue'
                        text = 'Missing keyword: %s' % k
                        break

            # test each of the basic keyword values
            if error == 0:
                # test service
                if self.kvp['service'] != 'CSW':
                    error = 1
                    locator = 'service'
                    code = 'InvalidParameterValue'
                    text = 'Invalid value for service: %s.\
                    Value MUST be CSW' % self.kvp['service']

                # test version
                kvp_version = self.kvp.get('version', '')
                kvp_version_integer = util.get_version_integer(kvp_version)
                if (request != 'GetCapabilities' and
                        kvp_version_integer != own_version_integer):
                    error = 1
                    locator = 'version'
                    code = 'InvalidParameterValue'
                    text = ('Invalid value for version: %s. Value MUST be '
                            '2.0.2 or 3.0.0' % self.kvp['version'])

                # check for GetCapabilities acceptversions
                if 'acceptversions' in self.kvp:
                    for vers in self.kvp['acceptversions'].split(','):
                        vers_integer = util.get_version_integer(vers)
                        if vers_integer == own_version_integer:
                            break
                        else:
                            error = 1
                            locator = 'acceptversions'
                            code = 'VersionNegotiationFailed'
                            text = ('Invalid parameter value in '
                                    'acceptversions: %s. Value MUST be '
                                    '2.0.2 or 3.0.0' %
                                    self.kvp['acceptversions'])

                # test request
                if request not in ops.keys():
                    error = 1
                    locator = 'request'
                    if request in ['Transaction', 'Harvest']:
                        code = 'OperationNotSupported'
                        text = '%s operations are not supported' % request
                    else:
                        code = 'InvalidParameterValue'
                        text = 'Invalid value for request: %s' % request

        if error == 1:  # return an ExceptionReport
            self.response = self.iface.exceptionreport(code, locator, text)

        else:  # process per the request value

            if 'responsehandler' in self.kvp:
                # set flag to process asynchronously
                import threading
                self.async = True
                request_id = self.kvp.get('requestid', None)
                if request_id is None:
                    import uuid
                    self.kvp['requestid'] = str(uuid.uuid4())

            if self.kvp['request'] == 'GetCapabilities':
                self.response = self.iface.getcapabilities()
            elif self.kvp['request'] == 'DescribeRecord':
                self.response = self.iface.describerecord()
            elif self.kvp['request'] == 'GetDomain':
                self.response = self.iface.getdomain()
            elif self.kvp['request'] == 'GetRecords':
                if self.async:  # process asynchronously
                    threading.Thread(target=self.iface.getrecords).start()
                    self.response = self.iface._write_acknowledgement()
                else:
                    self.response = self.iface.getrecords()
            elif self.kvp['request'] == 'GetRecordById':
                self.response = self.iface.getrecordbyid()
            elif self.kvp['request'] == 'GetRepositoryItem':
                self.response = self.iface.getrepositoryitem()
            elif self.kvp['request'] == 'Transaction':
                self.response = self.iface.transaction()
            elif self.kvp['request'] == 'Harvest':
                if self.async:  # process asynchronously
                    threading.Thread(target=self.iface.harvest).start()
                    self.response = self.iface._write_acknowledgement()
                else:
                    self.response = self.iface.harvest()
            else:
                self.response = self.iface.exceptionreport(
                    'InvalidParameterValue', 'request',
                    'Invalid request parameter: %s' % self.kvp['request']
                )

        if self.mode == 'sru':
            LOGGER.debug('SRU mode detected; processing response.')
            self.response = self.sru().response_csw2sru(self.response,
                                                        self.environ)
        elif self.mode == 'opensearch':
            LOGGER.debug('OpenSearch mode detected; processing response.')
            self.response = self.opensearch().response_csw2opensearch(
                self.response, self.config)

        elif self.mode == 'oaipmh':
            LOGGER.debug('OAI-PMH mode detected; processing response.')
            self.response = self.oaipmh().response(
                self.response, self.oaiargs, self.repository,
                self.config.get('server', 'url')
            )

        return self._write_response()

    def getcapabilities(self):
        """ Handle GetCapabilities request """
        return self.iface.getcapabilities()

    def describerecord(self):
        """ Handle DescribeRecord request """
        return self.iface.describerecord()

    def getdomain(self):
        """ Handle GetDomain request """
        return self.iface.getdomain()

    def getrecords(self):
        """ Handle GetRecords request """
        return self.iface.getrecords()

    def getrecordbyid(self, raw=False):
        """ Handle GetRecordById request """
        return self.iface.getrecordbyid()

    def getrepositoryitem(self):
        """ Handle GetRepositoryItem request """
        return self.iface.getrepositoryitem()

    def transaction(self):
        """ Handle Transaction request """
        return self.iface.transaction()

    def harvest(self):
        """ Handle Harvest request """
        return self.iface.harvest()

    def _write_response(self):
        """ Generate response """
        # set HTTP response headers and XML declaration

        xmldecl = ''
        appinfo = ''

        LOGGER.debug('Writing response.')

        if hasattr(self, 'soap') and self.soap:
            self._gen_soap_wrapper()

        if (isinstance(self.kvp, dict) and 'outputformat' in self.kvp and
                self.kvp['outputformat'] == 'application/json'):
            self.contenttype = self.kvp['outputformat']
            from pycsw.core.formats import fmt_json
            response = fmt_json.exml2json(self.response,
                                          self.context.namespaces,
                                          self.pretty_print)
        else:  # it's XML
            if 'outputformat' in self.kvp:
                self.contenttype = self.kvp['outputformat']
            else:
                self.contenttype = self.mimetype
            response = etree.tostring(self.response,
                                      pretty_print=self.pretty_print,
                                      encoding='unicode')
            xmldecl = ('<?xml version="1.0" encoding="%s" standalone="no"?>'
                       '\n' % self.encoding)
            appinfo = '<!-- pycsw %s -->\n' % self.context.version

        s = (u'%s%s%s' % (xmldecl, appinfo, response)).encode(self.encoding)
        LOGGER.debug('Response code: %s',
                     self.context.response_codes[self.status])
        LOGGER.debug('Response:\n%s', s)
        return [self.context.response_codes[self.status], s]

    def _gen_soap_wrapper(self):
        """ Generate SOAP wrapper """
        LOGGER.debug('Writing SOAP wrapper.')
        node = etree.Element(
            util.nspath_eval('soapenv:Envelope', self.context.namespaces),
            nsmap=self.context.namespaces
        )

        schema_location_ns = util.nspath_eval('xsi:schemaLocation',
                                              self.context.namespaces)
        node.attrib[schema_location_ns] = '%s %s' % (
            self.context.namespaces['soapenv'],
            self.context.namespaces['soapenv']
        )

        node2 = etree.SubElement(
            node, util.nspath_eval('soapenv:Body', self.context.namespaces))

        if self.exception:
            node3 = etree.SubElement(
                node2,
                util.nspath_eval('soapenv:Fault', self.context.namespaces)
            )
            node4 = etree.SubElement(
                node3,
                util.nspath_eval('soapenv:Code', self.context.namespaces)
            )

            etree.SubElement(
                node4,
                util.nspath_eval('soapenv:Value', self.context.namespaces)
            ).text = 'soap:Server'

            node4 = etree.SubElement(
                node3,
                util.nspath_eval('soapenv:Reason', self.context.namespaces)
            )

            etree.SubElement(
                node4,
                util.nspath_eval('soapenv:Text', self.context.namespaces)
            ).text = 'A server exception was encountered.'

            node4 = etree.SubElement(
                node3,
                util.nspath_eval('soapenv:Detail', self.context.namespaces)
            )
            node4.append(self.response)
        else:
            node2.append(self.response)

        self.response = node

    def _gen_manager(self):
        """ Update self.context.model with CSW-T advertising """
        if (self.config.has_option('manager', 'transactions') and
                self.config.get('manager', 'transactions') == 'true'):

            self.manager = True

            self.context.model['operations']['Transaction'] = {
                'methods': {'get': False, 'post': True},
                'parameters': {}
            }

            schema_values = [
                'http://www.opengis.net/cat/csw/2.0.2',
                'http://www.opengis.net/cat/csw/3.0',
                'http://www.opengis.net/wms',
                'http://www.opengis.net/wfs',
                'http://www.opengis.net/wcs',
                'http://www.opengis.net/wps/1.0.0',
                'http://www.opengis.net/sos/1.0',
                'http://www.opengis.net/sos/2.0',
                'http://www.isotc211.org/2005/gmi',
                'urn:geoss:waf',
            ]

            self.context.model['operations']['Harvest'] = {
                'methods': {'get': False, 'post': True},
                'parameters': {
                    'ResourceType': {'values': schema_values}
                }
            }

            self.context.model['operations']['Transaction'] = {
                'methods': {'get': False, 'post': True},
                'parameters': {
                    'TransactionSchemas': {'values': schema_values}
                }
            }

            self.csw_harvest_pagesize = 10
            if self.config.has_option('manager', 'csw_harvest_pagesize'):
                self.csw_harvest_pagesize = int(
                    self.config.get('manager', 'csw_harvest_pagesize'))

    def _test_manager(self):
        """ Verify that transactions are allowed """

        if self.config.get('manager', 'transactions') != 'true':
            raise RuntimeError('CSW-T interface is disabled')

        ipaddress = self.environ['REMOTE_ADDR']

        if self.config.has_option('manager', 'allowed_ips'):
            allowed_ips = self.config.get('manager', 'allowed_ips').split(',')
        else:
            allowed_ips = []
        ip_in_whitelist = util.ipaddress_in_whitelist(ipaddress, allowed_ips)
        if len(allowed_ips) > 0 and not ip_in_whitelist:
            raise RuntimeError('CSW-T operations not allowed for this '
                               'IP address: %s' % ipaddress)

    def _cql_update_queryables_mappings(self, cql, mappings):
        """ Transform CQL query's properties to underlying DB columns """
        LOGGER.debug('Raw CQL text = %s.' % cql)
        LOGGER.debug(str(mappings.keys()))
        if cql is not None:
            for key in mappings.keys():
                try:
                    cql = cql.replace(key, mappings[key]['dbcol'])
                except:
                    cql = cql.replace(key, mappings[key])
            LOGGER.debug('Interpolated CQL text = %s.' % cql)
            return cql

    def _process_responsehandler(self, xml):
        """ Process response handler """

        if self.kvp['responsehandler'] is not None:
            LOGGER.debug('Processing responsehandler %s.' %
                         self.kvp['responsehandler'])

            uprh = urlparse.urlparse(self.kvp['responsehandler'])

            if uprh.scheme == 'mailto':  # email
                import smtplib

                LOGGER.debug('Email detected.')

                smtp_host = 'localhost'
                if self.config.has_option('server', 'smtp_host'):
                    smtp_host = self.config.get('server', 'smtp_host')

                body = ('Subject: pycsw %s results\n\n%s' %
                        (self.kvp['request'], xml))

                try:
                    LOGGER.debug('Sending email.')
                    msg = smtplib.SMTP(smtp_host)
                    msg.sendmail(
                        self.config.get('metadata:main', 'contact_email'),
                        uprh.path, body
                    )
                    msg.quit()
                    LOGGER.debug('Email sent successfully.')
                except Exception as err:
                    LOGGER.debug('Error processing email: %s.' % str(err))

            elif uprh.scheme == 'ftp':
                import ftplib

                LOGGER.debug('FTP detected.')

                try:
                    LOGGER.debug('Sending to FTP server.')
                    ftp = ftplib.FTP(uprh.hostname)
                    if uprh.username is not None:
                        ftp.login(uprh.username, uprh.password)
                    ftp.storbinary('STOR %s' % uprh.path[1:], StringIO(xml))
                    ftp.quit()
                    LOGGER.debug('FTP sent successfully.')
                except Exception as err:
                    LOGGER.debug('Error processing FTP: %s.' % str(err))

    @staticmethod
    def normalize_kvp(kvp):
        """Normalize Key Value Pairs.

        This method will transform all keys to lowercase and leave values
        unchanged, as specified in the CSW standard (see for example note
        C on Table 62 - KVP Encoding for DescribeRecord operation request
        of the CSW standard version 2.0.2)

        :arg kvp: a mapping with Key Value Pairs
        :type kvp: dict
        :returns: A new dictionary with normalized parameters
        """

        result = dict()
        for name, value in kvp.items():
            result[name.lower()] = value
        return result
