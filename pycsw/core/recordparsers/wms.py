# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@gmail.com>
#
# Copyright (c) 2017 Tom Kralidis
# Copyright (c) 2017 Ricardo Garcia Silva
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

import logging

from owslib.util import build_get_url
from owslib.wms import WebMapService

from . import base

LOGGER = logging.getLogger(__name__)


def parse(context, repos, record, identifier, *args, **kwargs):
    records = []
    try:
        md = WebMapService(record, version='1.3.0')
    except Exception as err:
        LOGGER.info("Looks like WMS 1.3.0 is not supported; trying 1.1.1", err)
        md = WebMapService(record)
    records.append(base.generate_service_record(
        context=context,
        repos=repos,
        record=record,
        identifier=identifier,
        service_metadata=md,
        schema_url="http://www.opengis.net/wms",
        service_type="OGC:WMS",
        link_description="{},OGC-WMS Web Map Service,OGC:WMS".format(
            identifier)
    ))
    LOGGER.info('Harvesting {} WMS layers'.format(len(md.contents)))
    for layer_name, layer_metadata in md.contents.items():
        wkt_polygon, crs, distance_unit, bbox = base.get_service_layer_bbox(
            layer_metadata)
        links = "^".join((
            "{},OGC-Web Map Service,OGC:WMS,{}".format(layer_metadata.name,
                                                       md.url),
            build_wms_layer_thumbnail_link(layer_metadata.name, md.url, bbox)
        ))
        layer_info = base.get_service_layer_info(
            layer_metadata, identifier, record, md.url,
            links, crs, distance_unit
        )
        layer_record = base.generate_record(
            repos.dataset, layer_info, context,
            generate_iso_xml=True, metadata=md
        )
        records.append(layer_record)
    return records


def build_wms_layer_thumbnail_link(layer_name, url, bbox):
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