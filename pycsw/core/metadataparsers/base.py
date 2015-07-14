import logging

from ..etree import etree
from .. import util
# some more modules get imported in a lazy fashion, as needed.

LOGGER = logging.getLogger(__name__)


# TODO - Move these into the config module
NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'csw': 'http://www.opengis.net/cat/csw/2.0.2',
    'csw30': 'http://www.opengis.net/cat/csw/3.0',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dct': 'http://purl.org/dc/terms/',
    'dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    'fes20': 'http://www.opengis.net/fes/2.0',
    'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gmi': 'http://www.isotc211.org/2005/gmi',
    'gml': 'http://www.opengis.net/gml',
    'ogc': 'http://www.opengis.net/ogc',
    'os': 'http://a9.com/-/spec/opensearch/1.1/',
    'ows': 'http://www.opengis.net/ows',
    'ows11': 'http://www.opengis.net/ows/1.1',
    'ows20': 'http://www.opengis.net/ows/2.0',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'soapenv': 'http://www.w3.org/2003/05/soap-envelope',
    'xlink': 'http://www.w3.org/1999/xlink',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

def parse_records(record_description):
    """
    Parse a record into a models.Record instance

    :param record_description:
    :return:
    """

    if isinstance(record_description, str):
        exml = etree.fromstring(record_description)
    else:  # already serialized to lxml
        if hasattr(record_description, 'getroot'):  # standalone document
            exml = record_description.getroot()
        else:  # part of a larger document
            exml = record_description
    LOGGER.debug('Serialized metadata, parsing content model')
    parsing_class_path = {
        'metadata': "fgdc.FgdcParser",
        '{{{}}}MD_Metadata'.format(NAMESPACES['gmd']): "iso19139.IsoParser",
        '{{{}}}MI_Metadata'.format(NAMESPACES["gmi"]): "iso19139.IsoParser",
        '{{{}}}Record'.format(NAMESPACES["csw"]): "dublincore.DcParser",
        '{{{}}}RDF'.format(NAMESPACES["rdf"]): "dublincore.DcParser",
        '{{{}}}DIF'.format(NAMESPACES["dif"]): None,
    }.get(exml.tag)
    LOGGER.debug("parsing_class_path: {}".format(parsing_class_path))
    result = None
    try:
        relative_path = ".core.metadataparsers.{}".format(parsing_class_path)
        metadata_parser = util.import_class(relative_path,
                                            importlib_package="pycsw")
        result = metadata_parser.parse(exml)
    except TypeError as err:
        raise RuntimeError('Unsupported metadata format')
    return result if isinstance(result, list) else [result]
