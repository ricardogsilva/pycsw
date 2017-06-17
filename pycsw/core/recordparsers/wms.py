import logging

from owslib.util import build_get_url
from owslib.wms import WebMapService

from . import base
from .. import util

LOGGER = logging.getLogger(__name__)


def _parse_wms_service():
    pass


def parse_wms(context, repos, record, identifier, *args, **kwargs):
    records = []
    try:
        md = WebMapService(record, version='1.3.0')
    except Exception as err:
        LOGGER.info('Looks like WMS 1.3.0 is not supported; trying 1.1.1', err)
        md = WebMapService(record)
    wkt_polygon = _get_wms_service_wkt_polygon(md)
    # generate record of service instance
    service_info = base.get_general_service_info(
        metadata=md,
        identifier=identifier,
        record=record,
        typename="csw:Record",
        schema_url="http://www.opengis.net/wms",
        crs="urn:ogc:def:crs:EPSG:6.11:4326",
        distance_unit="degrees",
        service_type="OGC:WMS",
        coupling="tight"
    )
    service_links = [
        '{identifier},OGC-WMS Web Map Service,OGC:WMS,{url}'.format(
            identifier=identifier, url=md.url)
    ]
    service_info.update({
        "pycsw:Links": '^'.join(service_links),
        "pycsw:BoundingBox": wkt_polygon,
    })
    service_record = base.generate_record(
        repos.dataset,
        service_info,
        context,
        generate_iso_xml=True,
        metadata=md
    )
    records.append(service_record)
    # generate record foreach layer
    LOGGER.info('Harvesting {} WMS layers'.format(len(md.contents)))
    for layer_info in _get_wms_layers_info(metadata=md.contents,
                                           identifier=identifier,
                                           record=record,
                                           service_url=md.url):
        layer_record = base.generate_record(
            repos.dataset,
            layer_info,
            context,
            generate_iso_xml=True,
            metadata=md
        )
        records.append(layer_record)
    return records


def _get_wms_layers_info(metadata, identifier, record, service_url):
    for layer_name, layer_metadata in metadata.items():
        wkt_polygon, crs, distance_unit, bbox = _get_wms_layer_bbox(
            layer_metadata)
        begin, end = _get_wms_layer_temporal_info(layer_metadata.timepositions)
        thumbnail_link = _build_wms_layer_thumbnail_link(
            layer_metadata.name, service_url, bbox)
        layer_link = "{},OGC-Web Map Service,OGC:WMS,{}".format(
            layer_metadata.name, service_url),

        links = "^".join([layer_link, thumbnail_link]),
        info = base.get_general_info(
            metadata=layer_metadata,
            identifier=identifier,
            record=record,
            typename="csw:Record",
            schema_url="http://www.opengis.net/wms",
            crs=crs,
            distance_unit=distance_unit
        )
        info.update({
            "pycsw:TempExtent_begin": begin,
            "pycsw:TempExtent_end": end,
            "pycsw:Links": links,
        })
        yield info


def _get_wms_layer_bbox(layer_info):
    bbox = layer_info.boundingBoxWGS84
    wkt_polygon = None
    crs = None
    distance_units = None
    if bbox is not None:
        tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
        wkt_polygon = util.bbox2wktpolygon(tmp)
        crs = 'urn:ogc:def:crs:EPSG:6.11:4326'
        distance_units = 'degrees'
    else:
        bbox = layer_info.boundingBox
        if bbox:
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
            _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:%s' % \
                 bbox[-1].split(':')[1])
            wkt_polygon = util.bbox2wktpolygon(tmp)
            epsg_code = bbox[-1].split(":")[1]
            crs = 'urn:ogc:def:crs:EPSG:6.11:{}'.format(epsg_code)
    return wkt_polygon, crs, distance_units, bbox


def _get_wms_layer_temporal_info(time_positions):
    time_begin = time_end = None
    if len(time_positions) == 1 and len(time_positions[0].split('/')) > 1:
        time_envelope = time_positions[0].split('/')
        time_begin = time_envelope[0]
        time_end = time_envelope[1]
    elif len(time_positions) > 1:  # get first/last
        time_begin = time_positions[0]
        time_end = time_positions[-1]
    return time_begin, time_end


def _build_wms_layer_thumbnail_link(layer_name, url, bbox):
    params = {
        'service': 'WMS',
        'version': '1.1.1',
        'request': 'GetMap',
        'layers': layer_name,
        'format': 'image/png',
        'height': '200',
        'width': '200',
        'srs': 'EPSG:4326',
        'bbox':  '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3]),
        'styles': ''
    }
    thumbnail_url = build_get_url(url, params)
    return (
        "{},Web image thumbnail (URL),WWW:LINK-1.0-http--"
        "image-thumbnail,{}".format(layer_name, thumbnail_url)
    )


def _get_wms_service_wkt_polygon(metadata):
    for child_name, child_info in metadata.items():
        if child_info.parent is None:
            root_metadata = child_info
            break
    else:
        raise RuntimeError("Could not find root service metadata element")
    bbox = ",".join(str(i) for i in root_metadata.boundingBoxWGS84)
    return util.bbox2wktpolygon(bbox)

