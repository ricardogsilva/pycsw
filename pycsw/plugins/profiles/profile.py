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

import os
import warnings


class NewProfile(object):
    context = None
    name = ""
    version = ""
    title = ""
    url = ""
    extra_namespaces = dict()
    #namespace = ""
    typename = ""
    outputschema = ""
    prefixes = []
    mappings = dict()
    queryables = dict()

    update_operations = {
        "DescribeRecord": [("typename", typename)],
        "GetRecords": [("outputSchema", outputschema),
                       ("typenames", typename)],
        "GetRecordById": [("outputSchema", outputschema)],
        "Harvest": [("ResourceType", outputschema)],
    }

    def load_into_context(self, context):
        """Load the profile in the input context"""

        # update the context's namespaces with the ones defined in the profile
        # change the parameters of the operations defined in the context's models
        # add the outputschema to the context
        # add the queryables
        context.namespaces.update(self.extra_namespaces)
        self._update_context_operations(context)

    def unload_from_context(self, context):
        """Unload a profile from the input context"""
        pass

    def add_queryable(self, queryable):
        self.queryables[queryable.name] = queryable

    def _update_context_operations(self, context):
        """
        Update operation information on the input context's models

        :param operation_name:
        :param parameters:
        :return:
        """

        for model in context.csw_models.items():
            for op_name, parameter_pairs in self.update_operations.iteritems():
                op = model.operations.get(op_name)
                if op is not None:
                    for param_name, param_value in parameter_pairs:
                        op.parameters[param_name].values.append(param_value)


class Profile(object):
    ''' base Profile class '''
    def __init__(self, name, version, title, url,
    namespace, typename, outputschema, prefixes, model, core_namespaces,
    added_namespaces,repository):

        ''' Initialize profile '''
        self.name = name
        self.version = version
        self.title = title
        self.url = url
        self.namespace = namespace
        self.typename = typename
        self.outputschema = outputschema
        self.prefixes = prefixes
        self.repository = repository

        if 'DescribeRecord' in model['operations']:
            model['operations']['DescribeRecord']['parameters']\
            ['typeName']['values'].append(self.typename)

        model['operations']['GetRecords']['parameters']['outputSchema']\
        ['values'].append(self.outputschema)

        model['operations']['GetRecords']['parameters']['typeNames']\
        ['values'].append(self.typename)

        model['operations']['GetRecordById']['parameters']['outputSchema']\
        ['values'].append(self.outputschema)

        if 'Harvest' in model['operations']:
            model['operations']['Harvest']['parameters']['ResourceType']\
            ['values'].append(self.outputschema)

        # namespaces
        core_namespaces.update(added_namespaces)

        # repository
        model['typenames'][self.typename] = self.repository

    def extend_core(self, model, namespaces, config):
        ''' Extend config.model and config.namespaces '''
        raise NotImplementedError

    def check_parameters(self):
        ''' Perform extra parameters checking.
            Return dict with keys "locator", "code", "text" or None ''' 
        raise NotImplementedError

    def get_extendedcapabilities(self):
        ''' Return ExtendedCapabilities child as lxml.etree.Element '''
        raise NotImplementedError

    def get_schemacomponents(self):
        ''' Return schema components as lxml.etree.Element list '''
        raise NotImplementedError
    
    def check_getdomain(self, kvp):
        '''Perform extra profile specific checks in the GetDomain request'''
        raise NotImplementedError

    def write_record(self, result, esn, outputschema, queryables):
        ''' Return csw:SearchResults child as lxml.etree.Element '''
        raise NotImplementedError

    def transform2dcmappings(self, queryables):
        ''' Transform information model mappings into csw:Record mappings ''' 
        raise NotImplementedError

def load_profiles(path, cls, profiles):
    ''' load CSW profiles, return dict by class name ''' 

    def look_for_subclass(modulename):
        module = __import__(modulename)
 
        dmod = module.__dict__
        for modname in modulename.split('.')[1:]:
            dmod = dmod[modname].__dict__
 
        for key, entry in dmod.items():
            if key == cls.__name__:
                continue
 
            try:
                if issubclass(entry, cls):
                    aps['plugins'][key] = entry
            except TypeError:
                continue
 
    aps = {}
    aps['plugins'] = {}
    aps['loaded'] = {}

    for prof in profiles.split(','):
        # fgdc, atom, dif are supported in core
        # no need to specify them explicitly anymore
        # provide deprecation warning
        # https://github.com/geopython/pycsw/issues/118
        if prof in ['fgdc', 'atom', 'dif']:
            warnings.warn('%s is now a core module, and does not need to be'
                          ' specified explicitly.  So you can remove %s from '
                          'server.profiles' % (prof, prof))
        else: 
            modulename='%s.%s.%s' % (path.replace(os.sep, '.'), prof, prof)
            look_for_subclass(modulename)
    return aps
