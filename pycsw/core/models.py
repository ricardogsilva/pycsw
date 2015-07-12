"""
PyCSW models

Defines the structure of the database by using SQLAlchemy Declarative
"""

from sqlalchemy import (Column, Integer, Text, Sequence)
from sqlalchemy.ext.declarative import declarative_base


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

    f_table_catalog = Column(Text, nullable=False)
    f_table_schema = Column(Text, nullable=False)
    f_table_name = Column(Text, nullable=False)
    f_geometry_column = Column(Text, nullable=False)
    geometry_type = Column(Integer)
    coord_dimension = Column(Integer)
    srid = Column(Integer, nullable=False)
    geometry_format = Column(Text, nullable=False)


class Record(Base):
    __tablename__ = "records"

    identifier = Column(Text, Sequence("record_id_seq"), primary_key=True)
    typename = Column(Text, default='csw:Record', nullable=False, index=True)
    schema = Column(Text, default='http://www.opengis.net/cat/csw/2.0.2',
                    nullable=False, index=True)
    mdsource = Column(Text, default='local', nullable=False, index=True)
    insert_date = Column(Text, nullable=False, index=True)
    xml = Column(Text, nullable=False)
    anytext = Column(Text, nullable=False)
    language = Column(Text, index=True)

    # identification
    type = Column(Text, index=True)
    title = Column(Text, index=True)
    title_alternate = Column(Text, index=True)
    abstract = Column(Text, index=True)
    keywords = Column(Text, index=True)
    keywordstype = Column(Text, index=True)
    parentidentifier = Column(Text, index=True)
    relation = Column(Text, index=True)
    time_begin = Column(Text, index=True)
    time_end = Column(Text, index=True)
    topicategory = Column(Text, index=True)
    resourcelanguage = Column(Text, index=True)

    # attribution
    creator = Column(Text, index=True)
    publisher = Column(Text, index=True)
    contributor = Column(Text, index=True)
    organization = Column(Text, index=True)

    # security
    securityconstraints = Column(Text, index=True)
    accessconstraints = Column(Text, index=True)
    otherconstraints = Column(Text, index=True)

    # date
    date = Column(Text, index=True)
    date_revision = Column(Text, index=True)
    date_creation = Column(Text, index=True)
    date_publication = Column(Text, index=True)
    date_modified = Column(Text, index=True)

    format = Column(Text, index=True)
    source = Column(Text, index=True)

    # geospatial
    crs = Column(Text, index=True)
    geodescode = Column(Text, index=True)
    denominator = Column(Text, index=True)
    distancevalue = Column(Text, index=True)
    distanceuom = Column(Text, index=True)
    wkt_geometry = Column(Text)

    # service
    servicetype = Column(Text, index=True)
    servicetypeversion = Column(Text, index=True)
    operation = Column(Text, index=True)
    couplingtype = Column(Text, index=True)
    operateson = Column(Text, index=True)
    operatesonidentifier = Column(Text, index=True)
    operatesoname = Column(Text, index=True)

    # additional
    degree = Column(Text, index=True)
    classification = Column(Text, index=True)
    conditionapplyingtoaccessanduse = Column(Text, index=True)
    lineage = Column(Text, index=True)
    responsiblepartyrole = Column(Text, index=True)
    specificationtitle = Column(Text, index=True)
    specificationdate = Column(Text, index=True)
    specificationdatetype = Column(Text, index=True)

    # distribution
    # links: format "name,description,protocol,url[^,,,[^,,,]]"
    links = Column(Text, index=True)
