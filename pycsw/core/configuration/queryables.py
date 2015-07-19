from ..models import Record


class CswQueryable(object):
    name = ""
    map_to = ""
    xpath = ""

    def __init__(self, name, map_to, xpath=""):
        self.name = name
        self.map_to = map_to
        self.xpath = xpath

    def __repr__(self):
        return "{0}{1.__class__.__name__}({1.name!r}, {1.map_to!r})".format(
            __name__, self)


dc_title = CswQueryable('dc:title', Record.title)
dc_creator = CswQueryable('dc:creator',Record.creator)
dc_subject = CswQueryable('dc:subject', Record.keywords)
dct_abstract = CswQueryable('dct:abstract', Record.abstract)
dc_publisher = CswQueryable('dc:publisher', Record.publisher)
dc_contributor = CswQueryable('dc:contributor', Record.contributor)
dct_modified = CswQueryable('dct:modified', Record.date_modified)
dc_date = CswQueryable('dc:date', Record.date)
dc_type = CswQueryable('dc:type', Record.type)
dc_format = CswQueryable('dc:format', Record.format)
dc_identifier = CswQueryable('dc:identifier', Record.identifier)
dc_source = CswQueryable('dc:source', Record.source)
dc_language = CswQueryable('dc:language', Record.language)
dc_relation = CswQueryable('dc:relation', Record.relation)
dc_rights = CswQueryable('dc:rights', Record.accessconstraints)
ows_BoundingBox = CswQueryable('ows:BoundingBox', Record.wkt_geometry)
csw_AnyText = CswQueryable('csw:AnyText', Record.anytext)
dct_references = CswQueryable("dct_references", Record.links)
