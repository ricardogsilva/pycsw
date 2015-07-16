import logging
from uuid import uuid4

from owslib.wms import WebMapService

from .. import util
from ..models import Record
from ...plugins.profiles.apiso.apiso import APISO


LOGGER = logging.getLogger(__name__)


class WmsParser(object):

    def parse(self, url):
        md = WebMapService(url)
        records = []
        ident = uuid4().get_urn()
        service_record = Record(
            identifier=ident,
            typename='csw:Record',
            schema='http://www.opengis.net/wms',
            mdsource=url,
            insert_date=util.get_today_and_now(),
            anytext=util.get_anytext(md.getServiceXML()),
            type='service',
            title=md.identification.title,
            abstract=md.identification.abstract,
            keywords=','.join(md.identification.keywords),
            creator=md.provider.contact.name,
            publisher=md.provider.name,
            contributor=md.provider.contact.name,
            organization=md.provider.contact.name,
            accessconstraints=md.identification.accessconstraints,
            otherconstraints=md.identification.fees,
            source=url,
            format=md.identification.type,
            crs="urn:ogc:def:crs:EPSG:6.11:4326",
            distanceuom='degrees',
            servicetype='OGC:WMS',
            servicetypeversion=md.identification.version,
            operation=','.join([d.name for d in md.operations]),
            operateson=','.join(list(md.contents)),
            couplingtype='tight',
            links='{},OGC-WMS Web Map Service,OGC:WMS,{}'.format(
                ident, md.url),
        )
        service_record.xml = self.capabilities_to_iso(service_record, md, context))
        for c in md.contents:
            if md.contents[c].parent is None:
                bbox = md.contents[c].boundingBoxWGS84
                tmp = '{0[0]},{0[1]},{0[2]},{0[3]}'format(bbox)
                service_record.wkt_geometry = util.bbox2wktpolygon(tmp)
                break


    def capabilities_to_iso(self, record, capabilities, context):
        """Creates ISO metadata from Capabilities XML"""

        apiso_obj = APISO(context.model, context.namespaces, context)
        apiso_obj.ogc_schemas_base = 'http://schemas.opengis.net'
        apiso_obj.url = context.url
        queryables = dict(apiso_obj.repository['queryables']['SupportedISOQueryables'].items() + apiso_obj.repository['queryables']['SupportedISOQueryables'].items())
        iso_xml = apiso_obj.write_record(record, 'full', 'http://www.isotc211.org/2005/gmd', queryables, capabilities)
        return etree.tostring(iso_xml)



def _parse_wms(context, repos, record, identifier):

    from owslib.wms import WebMapService

    recobjs = []
    serviceobj = repos.dataset()

    md = WebMapService(record)

    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/wms')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(context, serviceobj, 'pycsw:AnyText', util.get_anytext(md.getServiceXML()))
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
    for c in md.contents:
        if md.contents[c].parent is None:
            bbox = md.contents[c].boundingBoxWGS84
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            _set(context, serviceobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
            break
    _set(context, serviceobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
    _set(context, serviceobj, 'pycsw:DistanceUOM', 'degrees')
    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:WMS')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:OperatesOn', ','.join(list(md.contents)))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-WMS Web Map Service,OGC:WMS,%s' % (identifier, md.url),
        ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))
    _set(context, serviceobj, 'pycsw:XML', caps2iso(serviceobj, md, context))

    recobjs.append(serviceobj)

    # generate record foreach layer

    LOGGER.debug('Harvesting %d WMS layers' % len(md.contents))

    for layer in md.contents:
        recobj = repos.dataset()
        identifier2 = '%s-%s' % (identifier, md.contents[layer].name)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wms')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'dataset')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        _set(context, recobj, 'pycsw:Title', md.contents[layer].title)
        _set(context, recobj, 'pycsw:Abstract', md.contents[layer].abstract)
        _set(context, recobj, 'pycsw:Keywords', ','.join(md.contents[layer].keywords))

        _set(context, recobj, 'pycsw:AnyText',
             util.get_anytext([md.contents[layer].title,
                               md.contents[layer].abstract,
                               ','.join(md.contents[layer].keywords)]))

        bbox = md.contents[layer].boundingBoxWGS84
        if bbox is not None:
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
            _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
            _set(context, recobj, 'pycsw:DistanceUOM', 'degrees')
        else:
            bbox = md.contents[layer].boundingBox
            if bbox:
                tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
                _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
                _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:%s' % \
                     bbox[-1].split(':')[1])

        params = {
            'service': 'WMS',
            'version': '1.1.1',
            'request': 'GetMap',
            'layers': md.contents[layer].name,
            'format': 'image/png',
            'height': '200',
            'width': '200',
            'srs': 'EPSG:4326',
            'bbox':  '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3]),
            'styles': ''
        }

        links = [
            '%s,OGC-Web Map Service,OGC:WMS,%s' % (md.contents[layer].name, md.url),
            '%s,Web image thumbnail (URL),WWW:LINK-1.0-http--image-thumbnail,%s' % (md.contents[layer].name, build_get_url(md.url, params))
        ]

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', caps2iso(recobj, md, context))

        recobjs.append(recobj)

    return recobjs
