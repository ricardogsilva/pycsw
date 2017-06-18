from .. import util
from ..etree import etree
from ...plugins.profiles.apiso.apiso import APISO


def caps2iso(record, caps, context):
    """Creates ISO metadata from Capabilities XML"""

    apiso_obj = APISO(context.model, context.namespaces, context)
    apiso_obj.ogc_schemas_base = 'http://schemas.opengis.net'
    apiso_obj.url = context.url
    queryables = dict(apiso_obj.repository['queryables']['SupportedISOQueryables'].items())
    iso_xml = apiso_obj.write_record(record, 'full', 'http://www.isotc211.org/2005/gmd', queryables, caps)
    return etree.tostring(iso_xml)


def generate_record(record_cls, info, context,
                     generate_iso_xml=True, metadata=None):
    record = record_cls()
    for field, value in info.items():
        if value is not None:
            setattr(record, context.md_core_model['mappings'][field], value)
    if generate_iso_xml:
        iso_metadata = caps2iso(record, metadata, context)
        setattr(
            record,
            context.md_core_model["mappings"]["pycsw:XML"],
            iso_metadata
        )
    return record


def get_general_info(metadata, identifier, record, typename, schema_url, crs,
                     distance_unit):
    return {
        "pycsw:Identifier": identifier,
        "pycsw:Typename": typename,
        "pycsw:Schema": schema_url,
        "pycsw:MdSource": record,
        "pycsw:InsertDate": util.get_today_and_now(),
        "pycsw:AnyText": util.get_anytext(metadata.getServiceXML()),
        "pycsw:Type": "dataset",
        "pycsw:Title": metadata.identification.title,
        "pycsw:Abstract": metadata.identification.abstract,
        "pycsw:Keywords": ','.join(metadata.identification.keywords),
        "pycsw:Creator": metadata.provider.contact.name,
        "pycsw:Publisher": metadata.provider.name,
        "pycsw:Contributor": metadata.provider.contact.name,
        "pycsw:OrganizationName": metadata.provider.contact.name,
        "pycsw:AccessConstraints": metadata.identification.accessconstraints,
        "pycsw:OtherConstraints": metadata.identification.fees,
        "pycsw:Source": record,
        "pycsw:Format": metadata.identification.type,
        "pycsw:CRS": crs,
        "pycsw:DistanceUOM": distance_unit,
    }


def get_general_service_info(metadata, identifier, record, typename,
                             schema_url, crs, distance_unit, service_type,
                             service_type_version, coupling):
    general_info = get_general_info(
        identifier, record, typename, schema_url, metadata)
    general_info.update({
        "pycsw:Type": "service",
        "pycsw:ServiceType": service_type,
        "pycsw:ServiceTypeVersion": metadata.identification.version,
        "pycsw:Operation": ','.join([d.name for d in metadata.operations]),
        "pycsw:OperatesOn": ','.join(list(metadata.contents)),
        "pycsw:CouplingType": coupling,
    })
    return general_info


def get_service_wkt_polygon(metadata):
    for child_name, child_info in metadata.items():
        if child_info.parent is None:
            root_metadata = child_info
            break
    else:
        raise RuntimeError("Could not find root service metadata element")
    bbox = ",".join(str(i) for i in root_metadata.boundingBoxWGS84)
    return util.bbox2wktpolygon(bbox)
