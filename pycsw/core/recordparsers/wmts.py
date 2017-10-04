import logging

from owslib.wmts import WebMapTileService
from owslib.util import build_get_url

from . import base

LOGGER = logging.getLogger(__name__)


# TODO - Differentiate between wmts version 1 in the parse() function
def parse(context, repos, record, identifier):
    records = []
    md = WebMapTileService(record)
    records.append(base.generate_service_record(
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
    LOGGER.debug('Harvesting {} WMTS layers'.format(len(md.contents)))
    for layer_name, layer_metadata in md.contents.items():
        wkt_polygon, crs, distance_unit, bbox = base.get_service_layer_bbox(
            layer_metadata)
        links = [
            "{},OGC-Web Map Tile Service,OGC:WMTS,{}".format(layer_metadata.name, md.url),
            build_wmts_layer_thumbnail_link(layer_metadata.name, md.url)
        ]
        layer_info = base.get_service_layer_info(
            layer_metadata, identifier, record, md.url, links,
            crs, distance_unit
        )
        layer_record = base.generate_record(
            repos.dataset, layer_info, context,
            generate_iso_xml=True, metadata=md
        )
        records.append(layer_record)
    return records


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
