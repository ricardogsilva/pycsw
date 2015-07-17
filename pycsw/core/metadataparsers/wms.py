import logging
from uuid import uuid4

from owslib.wms import WebMapService
from owslib.util import build_get_url

from ...plugins.profiles.apiso.apiso import APISO
from .. import util
from ..models import Record
from .ows import OwsParser


LOGGER = logging.getLogger(__name__)


class WmsParser(OwsParser):

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
            distanceuom='degrees',
            servicetype='OGC:WMS',
            servicetypeversion=md.identification.version,
            operation=','.join([d.name for d in md.operations]),
            operateson=','.join(list(md.contents)),
            couplingtype='tight',
            links='{},OGC-WMS Web Map Service,OGC:WMS,{}'.format(
                ident, md.url),
        )
        try:
            top = [v for k, v in md.contents.iteritems() if not v.parent].pop()
            wkt_geometry, crs_code = self._get_wkt_geometry(top)
            service_record.wkt_geometry = wkt_geometry
            service_record.crs = "urn:ogc:def:crs:EPSG:6.11:{}".format(
                crs_code)
        except IndexError:
            pass
        service_record.xml = self.capabilities_to_iso(service_record, md, context))  # TODO
        # now harvest individual layers
        LOGGER.debug('Harvesting %d WMS layers' % len(md.contents))
        for name, layer in md.contents.iteritems():
            layer_record = self.parse_wms_layer(layer)
            records.append(layer_record)
        records.append(service_record)
        return records

    def parse_wms_layer(self, md_layer, service_record):
        """Parse individual layer metadata from a WMS source

        :arg md_layer: A representation of the layer metadata, as parsed by
            owslib
        :type md_layer: owslib.wms.ContentMetadata
        :arg service_record: The parsed record for the whole WMS service
        :type service_record: pycsw.core.models.Record
        :return:
        """

        title = md_layer.title
        abstract = md_layer.abstract
        keywords = ",".join(md_layer.keywords)
        record = Record(
            identifier="{}-{}".format(service_record.identifier, md_layer.name),
            typename="csw:Record",
            schema='http://www.opengis.net/wms',  # replace with call to namespaces
            mdsource=service_record.mdsource,
            insert_date=util.get_today_and_now(),
            type='dataset',
            parentidentifier=service_record.identifier,
            title=title,
            abstract=abstract,
            keywords=keywords,
            anytext=util.get_anytext([title, abstract, keywords]),
        )
        wkt_geometry, crs_code = self._get_wkt_geometry(md_layer)
        if wkt_geometry is not None:
            record.wkt_geometry = wkt_geometry
            record.crs = "urn:ogc:def:crs:EPSG:6.11:{}".format(crs_code)
            record.distanceuom = "degrees" if crs_code == "4326" else None
        get_map_url = self.build_get_map_request(url=service_record.url,
                                                 layers=[md_layer.name],
                                                 bbox=wkt_geometry,
                                                 crs_code=crs_code)
        record.links = "^".join([
            "{},OGC-Web Map Service,OGC:WMS,{}".format(md_layer.name,
                                                       service_record.url),
            "{},Web image thumbnail (URL),WWW:LINK-1.0-"
            "http--image-thumbnail,{}".format(md_layer.name, get_map_url),
        ])
        record.xml = self.capabilities_to_iso(recobj, md, context))
        return record

    def build_get_map_request(self, url, layers=None, bbox=None,
                              wms_version="1.1.1", format="image/png",
                              width=200, height=200, crs_code="4326",
                              styles=""):
        layers = layers or []
        bbox = bbox or "-180,-90,180,90"
        all_inputs = locals().copy()
        del all_inputs["self"]
        del all_inputs["url"]
        return build_get_url(url, **all_inputs)
