import logging

from owslib.csw import CatalogueServiceWeb

from . import base
from .. import util

LOGGER = logging.getLogger(__name__)

# TODO - Differentiate between csw 2 and 3 in the parse() function

def parse_csw(context, repos, record, identifier, pagesize=10):
    """Parse a CSW record

    Parameters
    ----------
    context:
    repos:
    record:
    identifier:
    pagesize: int, optional

    Returns
    -------

    """

    if record.startswith("http"):
        LOGGER.info('CSW service detected, fetching via HTTP')
        try:
            result = _parse_csw_service(
                context, repos, record, identifier, pagesize)
        except Exception as err:
            # TODO: implement better exception handling
            if "ExceptionReport" in str(err):
                msg = 'CSW harvesting error: {}'.format(str(err))
                LOGGER.exception(msg)
                raise RuntimeError(msg)
            else:
                LOGGER.debug('Not a CSW, attempting to fetch Dublin Core')
                try:
                    content = util.http_request('GET', record)
                except Exception as err:
                    raise RuntimeError('HTTP error: {}'.format(str(err)))
                else:
                    parsed = _parse_dc(
                        context,
                        repos,
                        etree.fromstring(content, context.parser)
                    )
                    result = [parsed]
    else:  # csw:Record
        result = _parse_metadata(context, repos, record)
    return result


def _parse_csw_service(context, repos, record, identifier, pagesize):
    recobjs = []  # records
    serviceobj = repos.dataset()

    # if init raises error, this might not be a CSW
    md = CatalogueServiceWeb(record, timeout=60)

    LOGGER.info('Setting CSW service metadata')
    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/cat/csw/2.0.2')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(
        context,
        serviceobj,
        'pycsw:AnyText',
        util.get_anytext(md._exml)
    )
    _set(context, serviceobj, 'pycsw:Type', 'service')
    _set(context, serviceobj, 'pycsw:Title', md.identification.title)
    _set(context, serviceobj, 'pycsw:Abstract', md.identification.abstract)
    _set(context, serviceobj, 'pycsw:Keywords', ','.join(md.identification.keywords))
    _set(context, serviceobj, 'pycsw:Creator', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:Publisher', md.provider.name)
    _set(context, serviceobj, 'pycsw:Contributor', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:OrganizationName', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:AccessConstraints', md.identification.accessconstraints)
    _set(context, serviceobj, 'pycsw:OtherConstraints', md.identification.fees)
    _set(context, serviceobj, 'pycsw:Source', record)
    _set(context, serviceobj, 'pycsw:Format', md.identification.type)

    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:CSW')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-CSW Catalogue Service for the Web,OGC:CSW,%s' % (identifier, md.url)
    ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))
    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))

    recobjs.append(serviceobj)

    # get all supported typenames of metadata
    # so we can harvest the entire CSW

    # try for ISO, settle for Dublin Core
    csw_typenames = 'csw:Record'
    csw_outputschema = 'http://www.opengis.net/cat/csw/2.0.2'

    grop = md.get_operation_by_name('GetRecords')
    if all(['gmd:MD_Metadata' in grop.parameters['typeNames']['values'],
            'http://www.isotc211.org/2005/gmd' in grop.parameters['outputSchema']['values']]):
        LOGGER.debug('CSW supports ISO')
        csw_typenames = 'gmd:MD_Metadata'
        csw_outputschema = 'http://www.isotc211.org/2005/gmd'


    # now get all records
    # get total number of records to loop against

    try:
        md.getrecords2(typenames=csw_typenames, resulttype='hits',
                       outputschema=csw_outputschema)
        matches = md.results['matches']
    except:  # this is a CSW, but server rejects query
        raise RuntimeError(md.response)

    if pagesize > matches:
        pagesize = matches

    LOGGER.info('Harvesting %d CSW records', matches)

    # loop over all catalogue records incrementally
    for r in range(1, matches+1, pagesize):
        try:
            md.getrecords2(typenames=csw_typenames, startposition=r,
                           maxrecords=pagesize, outputschema=csw_outputschema, esn='full')
        except Exception as err:  # this is a CSW, but server rejects query
            raise RuntimeError(md.response)
        for k, v in md.records.items():
            # try to parse metadata
            try:
                LOGGER.info('Parsing metadata record: %s', v.xml)
                if csw_typenames == 'gmd:MD_Metadata':
                    recobjs.append(_parse_iso(context, repos,
                                              etree.fromstring(v.xml, context.parser)))
                else:
                    recobjs.append(_parse_dc(context, repos,
                                             etree.fromstring(v.xml, context.parser)))
            except Exception as err:  # parsing failed for some reason
                LOGGER.exception('Metadata parsing failed')

    return recobjs


# old implementation
def _parse_csw(context, repos, record, identifier, pagesize=10):

    from owslib.csw import CatalogueServiceWeb

    recobjs = []  # records
    serviceobj = repos.dataset()

    # if init raises error, this might not be a CSW
    md = CatalogueServiceWeb(record, timeout=60)

    LOGGER.info('Setting CSW service metadata')
    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/cat/csw/2.0.2')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(
        context,
        serviceobj,
        'pycsw:AnyText',
        util.get_anytext(md._exml)
    )
    _set(context, serviceobj, 'pycsw:Type', 'service')
    _set(context, serviceobj, 'pycsw:Title', md.identification.title)
    _set(context, serviceobj, 'pycsw:Abstract', md.identification.abstract)
    _set(context, serviceobj, 'pycsw:Keywords', ','.join(md.identification.keywords))
    _set(context, serviceobj, 'pycsw:Creator', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:Publisher', md.provider.name)
    _set(context, serviceobj, 'pycsw:Contributor', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:OrganizationName', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:AccessConstraints', md.identification.accessconstraints)
    _set(context, serviceobj, 'pycsw:OtherConstraints', md.identification.fees)
    _set(context, serviceobj, 'pycsw:Source', record)
    _set(context, serviceobj, 'pycsw:Format', md.identification.type)

    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:CSW')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-CSW Catalogue Service for the Web,OGC:CSW,%s' % (identifier, md.url)
    ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))
    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))

    recobjs.append(serviceobj)

    # get all supported typenames of metadata
    # so we can harvest the entire CSW

    # try for ISO, settle for Dublin Core
    csw_typenames = 'csw:Record'
    csw_outputschema = 'http://www.opengis.net/cat/csw/2.0.2'

    grop = md.get_operation_by_name('GetRecords')
    if all(['gmd:MD_Metadata' in grop.parameters['typeNames']['values'],
            'http://www.isotc211.org/2005/gmd' in grop.parameters['outputSchema']['values']]):
        LOGGER.debug('CSW supports ISO')
        csw_typenames = 'gmd:MD_Metadata'
        csw_outputschema = 'http://www.isotc211.org/2005/gmd'


    # now get all records
    # get total number of records to loop against

    try:
        md.getrecords2(typenames=csw_typenames, resulttype='hits',
                       outputschema=csw_outputschema)
        matches = md.results['matches']
    except:  # this is a CSW, but server rejects query
        raise RuntimeError(md.response)

    if pagesize > matches:
        pagesize = matches

    LOGGER.info('Harvesting %d CSW records', matches)

    # loop over all catalogue records incrementally
    for r in range(1, matches+1, pagesize):
        try:
            md.getrecords2(typenames=csw_typenames, startposition=r,
                           maxrecords=pagesize, outputschema=csw_outputschema, esn='full')
        except Exception as err:  # this is a CSW, but server rejects query
            raise RuntimeError(md.response)
        for k, v in md.records.items():
            # try to parse metadata
            try:
                LOGGER.info('Parsing metadata record: %s', v.xml)
                if csw_typenames == 'gmd:MD_Metadata':
                    recobjs.append(_parse_iso(context, repos,
                                              etree.fromstring(v.xml, context.parser)))
                else:
                    recobjs.append(_parse_dc(context, repos,
                                             etree.fromstring(v.xml, context.parser)))
            except Exception as err:  # parsing failed for some reason
                LOGGER.exception('Metadata parsing failed')

    return recobjs

