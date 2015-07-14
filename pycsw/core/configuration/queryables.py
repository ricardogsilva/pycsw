class CswQueryable(object):
    name = ""
    map_to = ""

    def __init__(self, name, map_to):
        self.name = name
        self.map_to = map_to


dc_title = CswQueryable('dc:title', 'pycsw:Title')
dc_creator = CswQueryable('dc:creator','pycsw:Creator')
dc_subject = CswQueryable('dc:subject', 'pycsw:Keywords')
dct_abstract = CswQueryable('dct:abstract', 'pycsw:Abstract')
dc_publisher = CswQueryable('dc:publisher', 'pycsw:Publisher')
dc_contributor = CswQueryable('dc:contributor', 'pycsw:Contributor')
dct_modified = CswQueryable('dct:modified', 'pycsw:Modified')
dc_date = CswQueryable('dc:date', 'pycsw:Date')
dc_type = CswQueryable('dc:type', 'pycsw:Type')
dc_format = CswQueryable('dc:format', 'pycsw:Format')
dc_identifier = CswQueryable('dc:identifier', 'pycsw:Identifier')
dc_source = CswQueryable('dc:source', 'pycsw:Source')
dc_language = CswQueryable('dc:language', 'pycsw:Language')
dc_relation = CswQueryable('dc:relation', 'pycsw:Relation')
dc_rights = CswQueryable('dc:rights', 'pycsw:AccessConstraints')
ows_BoundingBox = CswQueryable('ows:BoundingBox', 'pycsw:BoundingBox')
csw_AnyText = CswQueryable('csw:AnyText', 'pycsw:AnyText')

