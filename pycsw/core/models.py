"""
PyCSW models

Defines the structure of the database by using SQLAlchemy Declarative
"""

import logging

from sqlalchemy import (Column, Integer, Text, Sequence)
from sqlalchemy.ext.declarative import declarative_base


LOGGER = logging.getLogger(__name__)
Base = declarative_base()


class SpatialRefSys(Base):
    __tablename__ = "spatial_ref_sys"

    srid = Column(Integer, Sequence("spatial_ref_sys_id_seq"),
                  nullable=False, primary_key=True)
    auth_name = Column(Text)
    auth_srid = Column(Integer)
    srtext = Column(Text)


class GeometryColumn(Base):
    __tablename__ = "geometry_columns"

    f_table_name = Column(Text, nullable=False, primary_key=True)
    f_geometry_column = Column(Text, nullable=False, primary_key=True)
    f_table_catalog = Column(Text, nullable=False)
    f_table_schema = Column(Text, nullable=False)
    geometry_type = Column(Integer)
    coord_dimension = Column(Integer)
    srid = Column(Integer, nullable=False)
    geometry_format = Column(Text, nullable=False)


class Record(Base):
    """
    Database model for metadata records.

    This class follows sqlalchemy's declarative extension.

    In order to support multiple database schemas, the names of columns in
    the database can be mapped to the identifiers used in the mappings.

    Even if the actual SQL column names are dependent on the configured
    mappings, the attribute names of Record instances are constant. This allows
    pycsw to use a consistent interface to talk to the database table that
    holds metadata records.
    """

    __tablename__ = "records"

    # internal pycsw fields
    identifier = Column(Text, Sequence("record_id_seq"), primary_key=True,
                        doc="pycsw:Identifier")
    typename = Column(Text, default='csw:Record', doc="pycsw:Typename",
                      nullable=False, index=True)
    schema = Column(Text, doc="pycsw:Schema",
                    default='http://www.opengis.net/cat/csw/2.0.2',
                    nullable=False, index=True)
    mdsource = Column(Text, default='local', doc="pycsw:MdSource",
                      nullable=False, index=True)
    insert_date = Column(Text, nullable=False, doc="pycsw:InsertDate",
                         index=True)
    xml = Column(Text, doc="pycsw:XML", nullable=False)
    # CSW properties (queryables and returnables)
    anytext = Column(Text, doc="pycsw:AnyText", nullable=False)
    language = Column(Text, doc="pycsw:Language", index=True)
    type = Column(Text, doc="pycsw:Type", index=True)
    title = Column(Text, doc="pycsw:Title", index=True)
    title_alternate = Column(Text, doc="pycsw:AlternateTitle", index=True)
    abstract = Column(Text, doc="pycsw:Abstract", index=True)
    keywords = Column(Text, doc="pycsw:Keywords", index=True)
    keywordtype = Column(Text, doc="pycsw:KeywordType", index=True)
    parentidentifier = Column(Text, doc="pycsw:ParentIdentifier", index=True)
    relation = Column(Text, doc="pycsw:Relation", index=True)
    time_begin = Column(Text, doc="pycsw:TempExtent_begin", index=True)
    time_end = Column(Text, doc="pycsw:TempExtent_end", index=True)
    topicategory = Column(Text, doc="pycsw:TopicCategory", index=True)
    resourcelanguage = Column(Text, doc="pycsw:ResourceLanguage", index=True)
    # attribution
    creator = Column(Text, doc="pycsw:Creator", index=True)
    publisher = Column(Text, doc="pycsw:Publisher", index=True)
    contributor = Column(Text, doc="pycsw:Contributor", index=True)
    organization = Column(Text, doc="pycsw:OrganizationName", index=True)
    # security
    securityconstraints = Column(Text, doc="pycsw:SecurityConstraints",
                                 index=True)
    accessconstraints = Column(Text, doc="pycsw:AccessConstraints",
                               index=True)
    otherconstraints = Column(Text, doc="pycsw:OtherConstraints", index=True)
    # date
    date = Column(Text, doc="pycsw:Date", index=True)
    date_revision = Column(Text, doc="pycsw:RevisionDate", index=True)
    date_creation = Column(Text, doc="pycsw:CreationDate", index=True)
    date_publication = Column(Text, doc="pycsw:PublicationDate", index=True)
    date_modified = Column(Text, doc="pycsw:Modified", index=True)

    format = Column(Text, doc="pycsw:Format", index=True)
    source = Column(Text, doc="pycsw:Source", index=True)
    # geospatial
    crs = Column(Text, doc="pycsw:CRS", index=True)
    geodescode = Column(Text, doc="pycsw:GeographicDescriptionCode",
                        index=True)
    denominator = Column(Text, doc="pycsw:Denominator", index=True)
    distancevalue = Column(Text, doc="pycsw:DistanceValue", index=True)
    distanceuom = Column(Text, doc="pycsw:DistanceUOM", index=True)
    wkt_geometry = Column(Text, doc="pycsw:BoundingBox")
    # service
    servicetype = Column(Text, doc="pycsw:ServiceType", index=True)
    servicetypeversion = Column(Text, doc="pycsw:ServiceTypeVersion",
                                index=True)
    operation = Column(Text, doc="pycsw:Operation", index=True)
    couplingtype = Column(Text, doc="pycsw:CouplingType", index=True)
    operateson = Column(Text, doc="pycsw:OperatesOn", index=True)
    operatesonidentifier = Column(Text, doc="pycsw:OperatesOnIdentifier",
                                  index=True)
    operatesoname = Column(Text, doc="pycsw:OperatesOnName", index=True)
    # additional
    degree = Column(Text, doc="pycsw:Degree", index=True)
    classification = Column(Text, doc="pycsw:Classification", index=True)
    conditionapplyingtoaccessanduse = Column(
        Text, index=True, doc="pycsw:ConditionApplyingToAccessAndUse")
    lineage = Column(Text, doc="pycsw:Lineage", index=True)
    responsiblepartyrole = Column(Text, doc="pycsw:ResponsiblePartyRole",
                                  index=True)
    specificationtitle = Column(Text, doc="pycsw:SpecificationTitle" ,
                                index=True)
    specificationdate = Column(Text, doc="pycsw:SpecificationDate",
                               index=True)
    specificationdatetype = Column(Text, index=True,
                                   doc="pycsw:SpecificationDateType")
    # distribution
    # links: format "name,description,protocol,url[^,,,[^,,,]]"
    links = Column(Text, doc="pycsw:Links", index=True)

    @classmethod
    def remap_columns(cls, mappings):
        """Remap database column names to the input mappings.

        This function will remap the attributes of the Record class to
        different columns in the database.

        :arg mappings: a mapping where keys are the pycsw identifiers for
            each item in the md core model and the values are the names
            of the columns in the database where the values are stored
        :type mappings: dict
        """

        LOGGER.debug("remapping columns")
        for mapping_id, value in mappings.iteritems():
            for col in cls.__table__.columns:
                if mapping_id == col.doc:
                    col.name = value
