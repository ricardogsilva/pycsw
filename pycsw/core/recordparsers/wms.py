import logging

from owslib.util import build_get_url
from owslib.wms import WebMapService

from . import base
from .. import util

LOGGER = logging.getLogger(__name__)


def parse(context, repos, record, identifier, *args, **kwargs):
    records = []
    try:
        md = WebMapService(record, version='1.3.0')
    except Exception as err:
        LOGGER.info("Looks like WMS 1.3.0 is not supported; trying 1.1.1", err)
        md = WebMapService(record)
    records.append(
        _generate_service_record(context, repos, record, identifier, md))
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


def _generate_service_record(context, repos, record, identifier,
                             service_metadata):
    service_info = base.get_general_service_info(
        metadata=service_metadata,
        identifier=identifier,
        record=record,
        typename="csw:Record",
        schema_url="http://www.opengis.net/wms",
        crs="urn:ogc:def:crs:EPSG:6.11:4326",
        distance_unit="degrees",
        service_type="OGC:WMS",
        service_type_version=service_metadata.identification.version,
        coupling="tight"
    )
    service_links = [
        '{identifier},OGC-WMS Web Map Service,OGC:WMS,{url}'.format(
            identifier=identifier, url=service_metadata.url)
    ]
    service_info.update({
        "pycsw:Links": '^'.join(service_links),
        "pycsw:BoundingBox": base.get_service_wkt_polygon(service_metadata),
    })
    service_record = base.generate_record(
        repos.dataset,
        service_info,
        context,
        generate_iso_xml=True,
        metadata=service_metadata
    )
    return service_record


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
    try:
        bbox = ",".join(str(coord) for coord in layer_info.boundingBoxWGS84)
        crs = 'urn:ogc:def:crs:EPSG:6.11:4326'
        distance_unit = 'degrees'
    except TypeError:
        coords = layer_info.boundingBox[:-1]
        bbox = ",".join(str(coord) for coord in coords)
        epsg_code = layer_info.boundingBox[-1].split(":")[1]
        crs = "urn:ogc:def:crs:EPSG:6.11:{}".format(epsg_code)
        distance_unit = None
    wkt_polygon = util.bbox2wktpolygon(bbox)
    return wkt_polygon, crs, distance_unit, bbox


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
