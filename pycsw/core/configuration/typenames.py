from . import queryables


class ContextTypeName(object):
    name = "csw:Record"
    output_schema = ""
    queryables = {}

    def __init__(self, name, output_schema, queryables=None):
        self.name = name
        self.output_schema = output_schema
        for queryable in queryables:
            self.add_queryable(queryable)

    def add_queryable(self, queryable):
        self.queryables[queryable.name] = queryable

    def serialize(self):
        d = dict(outputschema=self.output_schema,
                 SupportedDublinCoreQueryables={})
        for name, queryable in self.queryables.iteritems():
            d["SupportedDublinCoreQueryables"][name] = {
                "dbcol": queryable.map_to}
        return d

    def __repr__(self):
        return ("{0}{1.__class__.__name__}({1.name!r}, {1.output_schema!r}, "
                "{1.queryables!r})".format(__name__, self))

    def __str__(self):
        return ("{0.__class__.__name__}({0.name}, "
                "{0.output_schema})".format(self))


csw_typename = ContextTypeName(
    "csw:Record",
    "http://www.opengis.net/cat/csw/2.0.2",
    queryables=[
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
)


csw3_typename = ContextTypeName(
    "csw:Record",
    "http://www.opengis.net/cat/csw/3.0",
    queryables=[
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
)
