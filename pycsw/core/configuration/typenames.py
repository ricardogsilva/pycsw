from . import queryables


class ContextTypeName(object):
    name = "csw:Record"
    output_schema = ""
    queryables = [
        queryables.dc_title,
        queryables.dc_creator,
        queryables.dc_subject,
        queryables.dct_abstract,
        queryables.dc_publisher,
        queryables.dc_contributor,
        queryables.dct_modified,
        queryables.dc_date,
        queryables.dc_type,
        queryables.dc_format,
        queryables.dc_identifier,
        queryables.dc_source,
        queryables.dc_language,
        queryables.dc_relation,
        queryables.dc_rights,
        queryables.ows_BoundingBox,
        queryables.csw_AnyText,
    ]

    def serialize(self):
        d = dict(outputschema=self.output_schema,
                 SupportedDublinCoreQueryables={})
        for q in self.queryables:
            d["SupportedDublinCoreQueryables"][q.name] = {"dbcol": q.map_to}
        return d


class CswContextTypeName(ContextTypeName):
    output_schema = "http://www.opengis.net/cat/csw/2.0.2"

class Csw3ContextTypeName(ContextTypeName):
    output_schema = "http://www.opengis.net/cat/csw/3.0"

csw_typename = CswContextTypeName()
csw3_typename = Csw3ContextTypeName()
