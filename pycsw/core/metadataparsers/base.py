import logging
from urlparse import urlparse

from ..etree import etree
from .. import util
from ..configuration.configuration import Context
# some more modules get imported in a lazy fashion, as needed.

LOGGER = logging.getLogger(__name__)


class MetadataParser(object):

    def parse_description(self, description, type_=None):
        records = []
        try:
            parsed_url = urlparse(description)
            if parsed_url.scheme == "http":
                records = self._parse_remote_description(description, type_)
            elif parsed_url.scheme == "":
                records = self._parse_local_description(description)
        except KeyError:
            # description is probably some form of metadata record already
            records = self._parse_local_description(description)
        return records

    def _parse_remote_description(self, description, type_):
        parsing_class_path = {
            'urn:geoss:waf': "waf.WafParser",
            'http://www.opengis.net/wms': "wms.WmsParser",
            'http://www.opengis.net/wps/1.0.0': "wps.WpsParser",
            'http://www.opengis.net/wfs': "wfs.WfsParser",
            'http://www.opengis.net/wcs': "wcs.WcsParser",
            'http://www.opengis.net/sos/1.0': "Sos.SosParser",
            'http://www.opengis.net/sos/2.0': "Sos.SosParser",
            'http://www.opengis.net/cat/csw/csdgm': "fgdc.FgdcParser",
        }[type_]
        relative_path = ".core.metadataparsers.{}".format(parsing_class_path)
        metadata_parser = util.import_class(relative_path,
                                            importlib_package="pycsw")
        result = metadata_parser.parse(description)
        return result if isinstance(result, list) else [result]

    def _parse_local_description(self, description):
        """
        Parse a local description.

        This method will create a list of `pycsw.core.models.Record` instances
        by parsing the input `record_description`.

        :param record_description: This input is very flexible. It can be one of
            * an already parsed ElementTree object
            * any of the formats accepted by `etree.parse()`, which includes

              * a filename/path
              * a file object
              * a file-like object
              * a URL using the HTTP or FTP protocol
        :return: a list of `pycsw.core.models.Record` instances
        :rtype: list
        """

        if not isinstance(description, etree._ElementTree):
            description = etree.parse(description)
        try:
            exml = description.getroot()  # standalone document
        except AttributeError:  # part of a larger document
            exml = description
        LOGGER.debug('Serialized metadata, parsing content model')
        ns = Context.namespaces
        parsing_class_path = {
            'metadata': "fgdc.FgdcParser",
            '{{{}}}MD_Metadata'.format(ns['gmd']): "iso19139.IsoParser",
            '{{{}}}MI_Metadata'.format(ns["gmi"]): "iso19139.IsoParser",
            '{{{}}}Record'.format(ns["csw"]): "dublincore.DcParser",
            '{{{}}}RDF'.format(ns["rdf"]): "dublincore.DcParser",
            '{{{}}}DIF'.format(ns["dif"]): None,
        }.get(exml.tag)
        LOGGER.debug("parsing_class_path: {}".format(parsing_class_path))
        result = None
        try:
            relative_path = ".core.metadataparsers.{}".format(
                parsing_class_path)
            metadata_parser = util.import_class(relative_path,
                                                importlib_package="pycsw")
            result = metadata_parser.parse(exml)
        except TypeError as err:
            raise RuntimeError('Unsupported metadata format')
        return result if isinstance(result, list) else [result]

