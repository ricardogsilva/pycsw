import logging

from owslib.wmts import WebMapTileService

from . import base

LOGGER = logging.getLogger(__name__)


# TODO - Differentiate between wmts version 1 in the parse() function
def parse(context, repos, record, identifier):

    recobjs = []
    serviceobj = repos.dataset()

    md = WebMapTileService(record)
    recobjs.append(base.generate_service_record(
        context=context,
        repos=repos,
        record=record,
        identifier=identifier,
        service_metadata=md,
        schema_url="http://www.opengis.net/wmts/1.0",
        service_type="OGC:WMTS",
        link_description="{},OGC-WMTS Web Map Service,OGC:WMTS".format(
            identifier)
    ))
    LOGGER.debug('Harvesting {} WMTS layers', len(md.contents))

    for layer in md.contents:
        recobj = repos.dataset()
        keywords = ''
        identifier2 = '%s-%s' % (identifier, md.contents[layer].name)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wmts/1.0')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'dataset')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        if md.contents[layer].title:
            _set(context, recobj, 'pycsw:Title', md.contents[layer].title)
        else:
            _set(context, recobj, 'pycsw:Title', "")
        if md.contents[layer].abstract:
            _set(context, recobj, 'pycsw:Abstract', md.contents[layer].abstract)
        else:
            _set(context, recobj, 'pycsw:Abstract', "")
        if hasattr(md.contents[layer], 'keywords'):  # safeguard against older OWSLib installs
            keywords = ','.join(md.contents[layer].keywords)
        _set(context, recobj, 'pycsw:Keywords', keywords)

        _set(
            context,
            recobj,
            'pycsw:AnyText',
            util.get_anytext([
                md.contents[layer].title,
                md.contents[layer].abstract,
                ','.join(keywords)
            ])
        )

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
            'service': 'WMTS',
            'version': '1.0.0',
            'request': 'GetTile',
            'layer': md.contents[layer].name,
        }

        links = [
            '%s,OGC-Web Map Tile Service,OGC:WMTS,%s' % (md.contents[layer].name, md.url),
            '%s,Web image thumbnail (URL),WWW:LINK-1.0-http--image-thumbnail,%s' % (md.contents[layer].name, build_get_url(md.url, params))
        ]

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))

        recobjs.append(recobj)

    return recobjs
