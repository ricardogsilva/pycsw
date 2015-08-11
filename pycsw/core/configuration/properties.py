"""
Property classes for pycsw.
"""

class CswProperty(object):
    name = ""
    maps_to = ""
    x_path = ""
    is_queryable = True
    is_returnable = True
    typenames = []
    elementsetnames = []

    def __init__(self, name, maps_to, x_path="", is_queryable=True,
                 is_returnable=True, typenames=None, elementsetnames=None):
        self.name = name
        self.maps_to = maps_to
        self.x_path = x_path if x_path != "" else name
        self.is_queryable = is_queryable
        self.is_returnable = is_returnable
        self.typenames = typenames or []
        self.elementsetnames = elementsetnames or []

    def __str__(self):
        return self.name