import logging

from owslib.wps import WebProcessingService
from owslib.util import build_get_url

from . import base

LOGGER = logging.getLogger(__name__)


# TODO - Differentiate between wps 1 and other versions the parse() function
def parse(context, repos, record, identifier):
    records = []
    md = WebProcessingService(record)
    records.append(base.generate_service_record(
        context=context,
        repos=repos,
        record=record,
        identifier=identifier,
        service_metadata=md,
        schema_url="http://www.opengis.net/wps/1.0.0",
        service_type="OGC:WPS",
        link_description="{},OGC-WMTS Web Map Service,OGC:WMTS".format(
            identifier)
    ))
    LOGGER.debug('Harvesting {} WPS processes'.format(len(md.processes)))
    for process in md.processes:



        recobj = repos.dataset()
        identifier2 = '%s-%s' % (identifier, process.identifier)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wps/1.0.0')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'software')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        _set(context, recobj, 'pycsw:Title', process.title)
        _set(context, recobj, 'pycsw:Abstract', process.abstract)

        _set(
            context,
            recobj,
            'pycsw:AnyText',
            util.get_anytext([process.title, process.abstract])
        )

        params = {
            'service': 'WPS',
            'version': '1.0.0',
            'request': 'DescribeProcess',
            'identifier': process.identifier
        }

        links.append(
            '%s,OGC-WPS DescribeProcess service (ver 1.0.0),OGC:WPS-1.0.0-http-describe-process,%s' % (identifier, build_get_url(md.url, {'service': 'WPS', 'version': '1.0.0', 'request': 'DescribeProcess', 'identifier': process.identifier})))

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))

        recobjs.append(recobj)

    return recobjs


def build_wmts_layer_thumbnail_link(layer_name, url):
    params = {
        'service': 'WMTS',
        'version': '1.0.0',
        'request': 'GetTile',
        'layers': layer_name,
    }
    thumbnail_url = build_get_url(url, params)
    return (
        "{},Web image thumbnail (URL),WWW:LINK-1.0-http--"
        "image-thumbnail,{}".format(layer_name, thumbnail_url)
    )
