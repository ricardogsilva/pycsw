# -*- coding: utf-8 -*-
# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#          Ricardo Garcia Silva <ricardo.garcia.silva@gmail.com>
#
# Copyright (c) 2017 Tom Kralidis
# Copyright (c) 2016 James F. Dickens
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
import uuid

from shapely.wkt import loads
from shapely.geometry import MultiPolygon

from .etree import etree
from . import util

LOGGER = logging.getLogger(__name__)


def parse(context, record, repos=None, mtype=None,
          identifier=None, pagesize=10):
    """Parse metadata

    Parameters
    ----------
    context:
    record: str
    repos:
    mtype: str, optional
    identifier: str, optional
    pagesize: int, optional

    Returns
    -------

    """

    identifier = identifier or uuid.uuid4().urn
    if mtype is None:
        result = parse_dataset_record(context, repos, record)
    else:
        result = parse_service_record(
            context, record, repos, mtype, identifier, pagesize=pagesize)
    return result


def parse_dataset_record(context, repos, record):
    """Parse metadata records in multiple formats"""

    if isinstance(record, str):
        exml = etree.fromstring(record, context.parser)
    else:  # already serialized to lxml
        if hasattr(record, 'getroot'):  # standalone document
            exml = record.getroot()
        else:  # part of a larger document
            exml = record

    tag = etree.QName(exml).localname
    LOGGER.info('Serialized metadata, parsing content model')
    handlers = {
        "MD_Metadata": "pycsw.core.recordparsers.iso.parse",
        "MI_Metadata": "pycsw.core.recordparsers.iso.parse",
        "metadata": "pycsw.core.recordparsers.fgdc.parse",
        "TRANSFER": "pycsw.core.recordparsers.gm03.parse",
        "Record": "pycsw.core.recordparsers.dublincore.parse",
        "RDF": "pycsw.core.recordparsers.dublincore.parse",
    }
    try:
        handler = util.lazy_load(handlers[tag])
    except KeyError:
        raise RuntimeError('Unsupported metadata format')
    else:
        return handler(context, repos, exml)


def parse_service_record(context, record, mtype, identifier,
                         repos, pagesize=10):
    handlers = {
        'http://www.opengis.net/cat/csw': "pycsw.core.recordparsers.csw.parse",
        'urn:geoss:waf': "pycsw.core.recordparsers.waf.parse",
        'http://www.opengis.net/wms': "pycsw.core.recordparsers.wms.parse",
        'http://www.opengis.net/wmts': "pycsw.core.recordparsers.wmts.parse",
        'http://www.opengis.net/wps': "pycsw.core.recordparsers.wps.parse",
        'http://www.opengis.net/wfs': "pycsw.core.recordparsers.wfs.parse",
        'http://www.opengis.net/wcs': "pycsw.core.recordparsers.wcs.parse",
        'http://www.opengis.net/sos': "pycsw.core.recordparsers.sos.parse",
        'http://www.opengis.net/cat/csw/csdgm': (
            "pycsw.core.recordparsers.fgdc.parse"),
    }
    for namespace, python_path in handlers.items():
        if namespace in mtype:
            handler = util.lazy_load(python_path)
            result = handler(
                context, repos, record, identifier, mtype,
                pagesize=pagesize
            )
            break
    else:  # could not find any handler to parse the metadata
        raise RuntimeError(
            "Unrecognized metadata type: {!r}".format(mtype))
    return result


def bbox_from_polygons(bboxs):
    """Derive an aggregated bbox from n polygons

    Parameters
    ----------
    bboxs: list
        A sequence of strings containing Well-Known Text representations of
        polygons

    Returns
    -------
    str
        Well-Known Text representation of the aggregated bounding box for
        all the input polygons
    """

    try:
        multi_pol = MultiPolygon(
            [loads(bbox) for bbox in bboxs]
        )
        bstr = ",".join(["{0:.2f}".format(b) for b in multi_pol.bounds])
        return util.bbox2wktpolygon(bstr)
    except Exception as err:
        raise RuntimeError('Cannot aggregate polygons: %s' % str(err))
