import datetime as dt
from uuid import uuid1

from .fields import TextField
from .fields import DateTimeField


class CswBoundingBox202:
    """Stores information regarding a resource's spatial extent.

    Attributes
    ----------
    west_bound_longitude: float
        Western-most coordinate of the limit of the resource's extent,
        expressed in longitude in decimal degrees (positive east).
    south_bound_latitude: float
        Southern-most coordinate of the limit of the resource's extent,
        expressed in latitude in decimal degrees (positive north).
    east_bound_longitude: float
        Eastern-most coordinate of the limit of the resource's extent,
        expressed in longitude in decimal degrees (positive east).
    north_bound_latitude: float
        Northern-most coordinate of the limit of the resource's extent,
        expressed in latitude in decimal degrees (positive north).

    """

    west_bound_longitude = 0
    south_bound_latitude = 0
    east_bound_longitude = 0
    north_bound_latitude = 0

    def __init__(self, west_longitude=0, south_latitude=0,
                 east_longitude=0, north_latitude=0):
        self.west_bound_longitude = west_longitude
        self.south_bound_latitude = south_latitude
        self.east_bound_longitude = east_longitude
        self.north_bound_latitude = north_latitude


class CswAssociation202:
    """Stores information regarding a resource's connection with others.

    Attributes
    ----------
    target: str
        Referenced resource.
    source: str
        Referencing resource.
    relation: str
        The name of the description of the relationship.
    """

    target = ""
    source = ""
    relation = ""

    def __init__(self, target, source, relation):
        self.target = target
        self.source = source
        self.relation = relation


class PycswRecord202:
    """Represents a CSW record, independent of its underlying data source.

    A record has all of the common **queryable** elements of the CSW general
    catalogue model, as defined in Table 1 of the CSW2.0.2 standard. It also
    has all of the common **returnable** properties, as defined in Table 4
    of the standard.

    The name of the class attributes follows as much as
    possible the names used in the standard for the OGC queryables, with the
    exception of the camelCase style being replaced by
    lowercaps_with_underscores, in order to be consistent with Python's
    practices.

    Attributes
    ----------
    subject: str
        The topic of the content of the resource.
    title: str
        A name given to the resource.
    abstract: str
        A summary of the content of the resource.
    any_text: str
        A target for full-text search of character data types in a catalogue.
    format_: str
        The physical or digital manifestation of the resource.
    identifier: str
        An unique reference to the record whithin the catalogue.
    modified: datetime.datetime
        Date on which the record was created or updated whithin the catalogue.
        NOTE: unlike the CSW standard, we are using a `datetime.datetime` type
        instead of a `datetime.date`.
    type_: str
        The nature or genre of the content of the resource. Type can include
        general categories, genres or aggregation levels of content.
    bounding_box: CswBoundingBox202
        A bounding box for identifying a geographic area of interest.
    crs: str, optional
        Geographic Coordinate System (Authority and ID) for the bounding box.
        Defaults to epsg:4326.
    association: CswAssociation202
        Complete statement of a one-to-one relationship between this resource
        and another one.
    creator: str
        An entity primarily responsible for making the content of the resource.
    publisher: str
        An entity responsible for making the resource available. This would
        equate to the Distributor in ISO and FGDC metadata.
    contributor: str
        An entity responsible for making contributions to the content of the
        resource.
    language: str
        A language of the intellectual content of the catalogue record.
    rights: str
        Information about rights held in and over the resource.
    """

    subject = TextField()
    title = TextField()
    abstract = TextField()
    format_ = TextField()
    identifier = TextField()
    modified = DateTimeField()
    type_ = TextField()
    bounding_box = TextField()  # FIXME: should probably be using a BoundingBoxField
    crs = TextField()
    association = TextField()  # FIXME: should probably be using an AssociationField
    creator = TextField()
    publisher = TextField()
    contributor = TextField()
    language = TextField()
    rights = TextField()

    def __init__(self, subject="", title="", abstract="", format_="",
                 identifier=None, type_="", bounding_box=None,
                 crs="epsg:4326", association=None, creator="", publisher="",
                 contributor="", language="", rights=""):
        self.subject = subject
        self.title = title
        self.abstract = abstract
        self.format_ = format_
        self.identifier = identifier or str(uuid1())
        self.modified = dt.datetime.utcnow()
        self.type_ = type_
        self.bounding_box = bounding_box
        self.crs = crs
        self.association = association
        self.creator = creator
        self.publisher = publisher
        self.contributor = contributor
        self.language = language
        self.rights = rights

    @property
    def any_text(self):
        pass


