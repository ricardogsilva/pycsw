"""GetCapabilities operation"""

from __future__ import absolute_import
import logging

from . import base
from ....core import util
from ....core.etree import etree
from ....exceptions import PycswError
from ....core import option


LOGGER = logging.getLogger(__name__)


class Capabilities(base.OperationResponseBase):
    filter_capabilities = None
    version = ""

    def __init__(self, pycsw_server, service_identification=True):
        super(Capabilities, self).__init__(pycsw_server)
        self.service_identification = service_identification

    def serialize(self):
        response = etree.Element(
            "{{{}}}Capabilities".format(self.pycsw_server.namespaces["csw"]),
            nsmap=self.pycsw_server.namespaces, version=self.version
        )
        response.set(
            "{{{}}}schemaLocation".format(self.pycsw_server.namespaces["xsi"]),
            "{} {}/csw/2.0.2/CSW-discovery.xsd'".format(
                self.pycsw_server.namespaces["ows_namespace"],
                self.pycsw_server.ogc_schemas_base
            )
        )
        # TODO - add the updateSequence attribute
        option_dict = {opt.name: opt for opt in option.pycsw_options}
        if self.service_identification:
            service_identification = self._get_service_identification(
                option_dict)
            response.append(service_identification)

    def _get_service_identification(self, option_dict):
        service_identification = etree.Element(
            "{{{}}}ServiceIdentification".format(
                self.pycsw_server.namespaces["ows"]),
            nsmap=self.pycsw_server.namespaces
        )
        for parameter_name in ("identfication_title",
                               "identification_abstract",
                               "identification_keywords",
                               "identification_keywords_type"):
            option_instance = option_dict[parameter_name]
            option_element = option_instance.to_xml(self.pycsw_server)
            service_identification.append(option_element)
        return service_identification


        metadata_main = dict(self.parent.config.items('metadata:main'))

        if serviceidentification:
            LOGGER.debug('Writing section ServiceIdentification.')

            serviceidentification = etree.SubElement(node, \
                                                     util.nspath_eval('ows:ServiceIdentification',
                                                                      self.parent.context.namespaces))

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Title', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_title', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Abstract', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_abstract', 'missing')

            keywords = etree.SubElement(serviceidentification,
                                        util.nspath_eval('ows:Keywords', self.parent.context.namespaces))

            for k in \
                    metadata_main.get('identification_keywords').split(','):
                etree.SubElement(
                    keywords, util.nspath_eval('ows:Keyword',
                                               self.parent.context.namespaces)).text = k

            etree.SubElement(keywords,
                             util.nspath_eval('ows:Type', self.parent.context.namespaces),
                             codeSpace='ISOTC211/19115').text = \
                metadata_main.get('identification_keywords_type', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:ServiceType', self.parent.context.namespaces),
                             codeSpace='OGC').text = 'CSW'

            for stv in self.parent.context.model['parameters']['version']['values']:
                etree.SubElement(serviceidentification,
                                 util.nspath_eval('ows:ServiceTypeVersion',
                                                  self.parent.context.namespaces)).text = stv

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Fees', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_fees', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:AccessConstraints',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('identification_accessconstraints', 'missing')


class GetCapabilities(base.OperationRequestBase):
    name = "GetCapabilities"
    allowed_http_methods = (util.HTTP_GET,)
    sections = ["ServiceIdentification", "ServiceProvider",
                "OperationsMetadata", "Filter_Capabilities"]

    def validate_kvp(self, parameters):
        requested_sections = parameters.get("sections", "").split(",")
        requested_versions = parameters.get("acceptVersions", "").split(",")
        requested_accept_formats = parameters.get(
            "acceptFormats", "text/xml").split(",")
        validated_parameters = {
            # updateSequence - optional
            # acceptLanguages - optional
            "acceptFormats": requested_accept_formats,
            "acceptVersions": self._validate_accept_versions(
                requested_versions),
            "sections": self._validate_sections(requested_sections),
        }
        return validated_parameters

    def _validate_sections(self, requested_sections):
        for requested in requested_sections:
            if requested not in self.sections:
                raise PycswError("", "", "", "Invalid section")
        return requested_sections

    def _validate_accept_versions(self, requested_versions):
        for version in requested_versions:
            if version not in self.pycsw_server.accept_versions:
                raise PycswError("", "", "", "Invalid accept version")
        return requested_versions

    def validate_xml(self, request_body):
        raise NotImplementedError

    def process_request(self, cleaned_request):
        # As an intermediary version, we're using the previous implementation
        # mostly unchanged. The next move is to reimplement using the
        # validate_kvp() and process_kvp() methods
        #return self._get_capabilities(cleaned_request)
        write_service_identification = ("ServiceIdentification" in
                                        cleaned_request["sections"])
        response = Capabilities(
            self.pycsw_server,
            service_identification=write_service_identification,
        )
        response.serialize()

    def _get_capabilities(self, request):
        """Handle GetCapabilities request"""

        service_identification = True
        service_provider = True
        operations_metadata = True

        if 'sections' in request.GET:
            serviceidentification = False
            serviceprovider = False
            operationsmetadata = False
            for section in request.GET["sections"].split(','):
                if section == 'ServiceIdentification':
                    serviceidentification = True
                if section == 'ServiceProvider':
                    serviceprovider = True
                if section == 'OperationsMetadata':
                    operationsmetadata = True

        # check extra parameters that may be def'd by profiles
        if self.pycsw_server.profiles is not None:
            for prof in self.pycsw_server.profiles['loaded'].keys():
                result = \
                    self.pycsw_server.profiles['loaded'][prof].check_parameters(request.GET)
                if result is not None:
                    raise PycswError(self.pycsw_server, result["code"],
                                     result["locator"], result["text"])

        # @updateSequence: get latest update to repository
        try:
            updatesequence = \
                util.get_time_iso2unix(self.parent.repository.query_insert())
        except:
            updatesequence = None

        node = etree.Element(util.nspath_eval('csw:Capabilities',
                                              self.parent.context.namespaces),
                             nsmap=self.parent.context.namespaces, version='2.0.2',
                             updateSequence=str(updatesequence))

        if 'updatesequence' in self.parent.kvp:
            if int(self.parent.kvp['updatesequence']) == updatesequence:
                return node
            elif int(self.parent.kvp['updatesequence']) > updatesequence:
                return self.exceptionreport('InvalidUpdateSequence',
                                            'updatesequence',
                                            'outputsequence specified (%s) is higher than server\'s \
                                            updatesequence (%s)' % (self.parent.kvp['updatesequence'],
                                                                    updatesequence))

        node.attrib[util.nspath_eval('xsi:schemaLocation',
                                     self.parent.context.namespaces)] = '%s %s/csw/2.0.2/CSW-discovery.xsd' % \
                                                                        (self.parent.context.namespaces['csw'],
                                                                         self.parent.config.get('server', 'ogc_schemas_base'))

        metadata_main = dict(self.parent.config.items('metadata:main'))

        if serviceidentification:
            LOGGER.debug('Writing section ServiceIdentification.')

            serviceidentification = etree.SubElement(node, \
                                                     util.nspath_eval('ows:ServiceIdentification',
                                                                      self.parent.context.namespaces))

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Title', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_title', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Abstract', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_abstract', 'missing')

            keywords = etree.SubElement(serviceidentification,
                                        util.nspath_eval('ows:Keywords', self.parent.context.namespaces))

            for k in \
                    metadata_main.get('identification_keywords').split(','):
                etree.SubElement(
                    keywords, util.nspath_eval('ows:Keyword',
                                               self.parent.context.namespaces)).text = k

            etree.SubElement(keywords,
                             util.nspath_eval('ows:Type', self.parent.context.namespaces),
                             codeSpace='ISOTC211/19115').text = \
                metadata_main.get('identification_keywords_type', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:ServiceType', self.parent.context.namespaces),
                             codeSpace='OGC').text = 'CSW'

            for stv in self.parent.context.model['parameters']['version']['values']:
                etree.SubElement(serviceidentification,
                                 util.nspath_eval('ows:ServiceTypeVersion',
                                                  self.parent.context.namespaces)).text = stv

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:Fees', self.parent.context.namespaces)).text = \
                metadata_main.get('identification_fees', 'missing')

            etree.SubElement(serviceidentification,
                             util.nspath_eval('ows:AccessConstraints',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('identification_accessconstraints', 'missing')

        if serviceprovider:
            LOGGER.debug('Writing section ServiceProvider.')
            serviceprovider = etree.SubElement(node,
                                               util.nspath_eval('ows:ServiceProvider', self.parent.context.namespaces))

            etree.SubElement(serviceprovider,
                             util.nspath_eval('ows:ProviderName', self.parent.context.namespaces)).text = \
                metadata_main.get('provider_name', 'missing')

            providersite = etree.SubElement(serviceprovider,
                                            util.nspath_eval('ows:ProviderSite', self.parent.context.namespaces))

            providersite.attrib[util.nspath_eval('xlink:type',
                                                 self.parent.context.namespaces)] = 'simple'

            providersite.attrib[util.nspath_eval('xlink:href',
                                                 self.parent.context.namespaces)] = \
                metadata_main.get('provider_url', 'missing')

            servicecontact = etree.SubElement(serviceprovider,
                                              util.nspath_eval('ows:ServiceContact', self.parent.context.namespaces))

            etree.SubElement(servicecontact,
                             util.nspath_eval('ows:IndividualName',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_name', 'missing')

            etree.SubElement(servicecontact,
                             util.nspath_eval('ows:PositionName',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_position', 'missing')

            contactinfo = etree.SubElement(servicecontact,
                                           util.nspath_eval('ows:ContactInfo', self.parent.context.namespaces))

            phone = etree.SubElement(contactinfo, util.nspath_eval('ows:Phone',
                                                                   self.parent.context.namespaces))

            etree.SubElement(phone, util.nspath_eval('ows:Voice',
                                                     self.parent.context.namespaces)).text = \
                metadata_main.get('contact_phone', 'missing')

            etree.SubElement(phone, util.nspath_eval('ows:Facsimile',
                                                     self.parent.context.namespaces)).text = \
                metadata_main.get('contact_fax', 'missing')

            address = etree.SubElement(contactinfo,
                                       util.nspath_eval('ows:Address', self.parent.context.namespaces))

            etree.SubElement(address,
                             util.nspath_eval('ows:DeliveryPoint',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_address', 'missing')

            etree.SubElement(address, util.nspath_eval('ows:City',
                                                       self.parent.context.namespaces)).text = \
                metadata_main.get('contact_city', 'missing')

            etree.SubElement(address,
                             util.nspath_eval('ows:AdministrativeArea',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_stateorprovince', 'missing')

            etree.SubElement(address,
                             util.nspath_eval('ows:PostalCode',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_postalcode', 'missing')

            etree.SubElement(address,
                             util.nspath_eval('ows:Country', self.parent.context.namespaces)).text = \
                metadata_main.get('contact_country', 'missing')

            etree.SubElement(address,
                             util.nspath_eval('ows:ElectronicMailAddress',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_email', 'missing')

            url = etree.SubElement(contactinfo,
                                   util.nspath_eval('ows:OnlineResource', self.parent.context.namespaces))

            url.attrib[util.nspath_eval('xlink:type',
                                        self.parent.context.namespaces)] = 'simple'

            url.attrib[util.nspath_eval('xlink:href',
                                        self.parent.context.namespaces)] = \
                metadata_main.get('contact_url', 'missing')

            etree.SubElement(contactinfo,
                             util.nspath_eval('ows:HoursOfService',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_hours', 'missing')

            etree.SubElement(contactinfo,
                             util.nspath_eval('ows:ContactInstructions',
                                              self.parent.context.namespaces)).text = \
                metadata_main.get('contact_instructions', 'missing')

            etree.SubElement(servicecontact,
                             util.nspath_eval('ows:Role', self.parent.context.namespaces),
                             codeSpace='ISOTC211/19115').text = \
                metadata_main.get('contact_role', 'missing')

        if operationsmetadata:
            LOGGER.debug('Writing section OperationsMetadata.')
            operationsmetadata = etree.SubElement(node,
                                                  util.nspath_eval('ows:OperationsMetadata',
                                                                   self.parent.context.namespaces))

            for operation in self.parent.context.model['operations'].keys():
                oper = etree.SubElement(operationsmetadata,
                                        util.nspath_eval('ows:Operation', self.parent.context.namespaces),
                                        name=operation)

                dcp = etree.SubElement(oper, util.nspath_eval('ows:DCP',
                                                              self.parent.context.namespaces))

                http = etree.SubElement(dcp, util.nspath_eval('ows:HTTP',
                                                              self.parent.context.namespaces))

                if self.parent.context.model['operations'][operation]['methods']['get']:
                    get = etree.SubElement(http, util.nspath_eval('ows:Get',
                                                                  self.parent.context.namespaces))

                    get.attrib[util.nspath_eval('xlink:type', \
                                                self.parent.context.namespaces)] = 'simple'

                    get.attrib[util.nspath_eval('xlink:href', \
                                                self.parent.context.namespaces)] = self.parent.config.get('server', 'url')

                if self.parent.context.model['operations'][operation]['methods']['post']:
                    post = etree.SubElement(http, util.nspath_eval('ows:Post',
                                                                   self.parent.context.namespaces))
                    post.attrib[util.nspath_eval('xlink:type',
                                                 self.parent.context.namespaces)] = 'simple'
                    post.attrib[util.nspath_eval('xlink:href',
                                                 self.parent.context.namespaces)] = \
                        self.parent.config.get('server', 'url')

                for parameter in \
                        self.parent.context.model['operations'][operation]['parameters']:
                    param = etree.SubElement(oper,
                                             util.nspath_eval('ows:Parameter',
                                                              self.parent.context.namespaces), name=parameter)

                    for val in \
                            self.parent.context.model['operations'][operation] \
                                    ['parameters'][parameter]['values']:
                        etree.SubElement(param,
                                         util.nspath_eval('ows:Value',
                                                          self.parent.context.namespaces)).text = val

                if operation == 'GetRecords':  # advertise queryables
                    for qbl in self.parent.repository.queryables.keys():
                        if qbl != '_all':
                            param = etree.SubElement(oper,
                                                     util.nspath_eval('ows:Constraint',
                                                                      self.parent.context.namespaces), name=qbl)

                            for qbl2 in self.parent.repository.queryables[qbl]:
                                etree.SubElement(param,
                                                 util.nspath_eval('ows:Value',
                                                                  self.parent.context.namespaces)).text = qbl2

                    if self.parent.profiles is not None:
                        for con in self.parent.context.model[ \
                                'operations']['GetRecords']['constraints'].keys():
                            param = etree.SubElement(oper,
                                                     util.nspath_eval('ows:Constraint',
                                                                      self.parent.context.namespaces), name = con)
                            for val in self.parent.context.model['operations'] \
                                    ['GetRecords']['constraints'][con]['values']:
                                etree.SubElement(param,
                                                 util.nspath_eval('ows:Value',
                                                                  self.parent.context.namespaces)).text = val

            for parameter in self.parent.context.model['parameters'].keys():
                param = etree.SubElement(operationsmetadata,
                                         util.nspath_eval('ows:Parameter', self.parent.context.namespaces),
                                         name=parameter)

                for val in self.parent.context.model['parameters'][parameter]['values']:
                    etree.SubElement(param, util.nspath_eval('ows:Value',
                                                             self.parent.context.namespaces)).text = val

            for constraint in self.parent.context.model['constraints'].keys():
                param = etree.SubElement(operationsmetadata,
                                         util.nspath_eval('ows:Constraint', self.parent.context.namespaces),
                                         name=constraint)

                for val in self.parent.context.model['constraints'][constraint]['values']:
                    etree.SubElement(param, util.nspath_eval('ows:Value',
                                                             self.parent.context.namespaces)).text = val

            if self.parent.profiles is not None:
                for prof in self.parent.profiles['loaded'].keys():
                    ecnode = \
                        self.parent.profiles['loaded'][prof].get_extendedcapabilities()
                    if ecnode is not None:
                        operationsmetadata.append(ecnode)

        # always write out Filter_Capabilities
        LOGGER.debug('Writing section Filter_Capabilities.')
        fltcaps = etree.SubElement(node,
                                   util.nspath_eval('ogc:Filter_Capabilities', self.parent.context.namespaces))

        spatialcaps = etree.SubElement(fltcaps,
                                       util.nspath_eval('ogc:Spatial_Capabilities', self.parent.context.namespaces))

        geomops = etree.SubElement(spatialcaps,
                                   util.nspath_eval('ogc:GeometryOperands', self.parent.context.namespaces))

        for geomtype in \
                fes1.MODEL['GeometryOperands']['values']:
            etree.SubElement(geomops,
                             util.nspath_eval('ogc:GeometryOperand',
                                              self.parent.context.namespaces)).text = geomtype

        spatialops = etree.SubElement(spatialcaps,
                                      util.nspath_eval('ogc:SpatialOperators', self.parent.context.namespaces))

        for spatial_comparison in \
                fes1.MODEL['SpatialOperators']['values']:
            etree.SubElement(spatialops,
                             util.nspath_eval('ogc:SpatialOperator', self.parent.context.namespaces),
                             name=spatial_comparison)

        scalarcaps = etree.SubElement(fltcaps,
                                      util.nspath_eval('ogc:Scalar_Capabilities', self.parent.context.namespaces))

        etree.SubElement(scalarcaps, util.nspath_eval('ogc:LogicalOperators',
                                                      self.parent.context.namespaces))

        cmpops = etree.SubElement(scalarcaps,
                                  util.nspath_eval('ogc:ComparisonOperators', self.parent.context.namespaces))

        for cmpop in fes1.MODEL['ComparisonOperators'].keys():
            etree.SubElement(cmpops,
                             util.nspath_eval('ogc:ComparisonOperator',
                                              self.parent.context.namespaces)).text = \
                fes1.MODEL['ComparisonOperators'][cmpop]['opname']

        arithops = etree.SubElement(scalarcaps,
                                    util.nspath_eval('ogc:ArithmeticOperators', self.parent.context.namespaces))

        functions = etree.SubElement(arithops,
                                     util.nspath_eval('ogc:Functions', self.parent.context.namespaces))

        functionames = etree.SubElement(functions,
                                        util.nspath_eval('ogc:FunctionNames', self.parent.context.namespaces))

        for fnop in sorted(fes1.MODEL['Functions'].keys()):
            etree.SubElement(functionames,
                             util.nspath_eval('ogc:FunctionName', self.parent.context.namespaces),
                             nArgs=fes1.MODEL['Functions'][fnop]['args']).text = fnop

        idcaps = etree.SubElement(fltcaps,
                                  util.nspath_eval('ogc:Id_Capabilities', self.parent.context.namespaces))

        for idcap in fes1.MODEL['Ids']['values']:
            etree.SubElement(idcaps, util.nspath_eval('ogc:%s' % idcap,
                                                      self.parent.context.namespaces))

        return node

