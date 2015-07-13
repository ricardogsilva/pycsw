import logging

from sqlalchemy import text, func

from .. import models
from ..models import Record
from .. import util
from .decorators import sqlalchemy_transaction


LOGGER = logging.getLogger(__name__)


class RepositoryHandler(object):
    engine = None
    session = None
    filter = None
    context = None

    def __init__(self, engine, session):
        """Base implementation for dealing with database operations.

        Specialized classes deal with issues specific to each database backend,
        typically associated with the initial creation of each database.

        The management of records and execution of queries can be made by
        interacting directly with this class.
        """

        self.engine = engine
        self.session = session

    def create_db(self):
        # sqlalchemy's create_all() method will not attempt to recreate tables
        # already present in the database, therefore our spatial_ref_sys and
        # geometry_columns tables will only be created if needed
        models.Base.metadata.create_all(self.engine)

    def populate_spatial_ref_sys(self):
        record = models.SpatialRefSys(
            srid=4326, auth_name="EPSG", auth_srid=4326,
            srtext='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",'
                   '6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY'
                   '["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY'
                   '["EPSG","8901"]],UNIT["degree",0.01745329251994328,'
                   'AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
        )
        self.session.add(record)

    def populate_geometry_columns(self):
        record = models.GeometryColumn(
            f_table_catalog="public", f_table_schema="public",
            f_table_name=Record.__tablename__,
            f_geometry_column="wkt_geometry",
            geometry_type=3, coord_dimension=2, srid=4326,
            geometry_format="WKT"
        )
        self.session.add(record)

    def setup_db(self, commit=True):
        """
        Setup the actual database to be used by pycsw.

        :param commit: Should the session be committed?
        :type commit: bool
        """

        self.create_db()
        self.populate_spatial_ref_sys()
        self.populate_geometry_columns()
        if commit:
            self.session.commit()

    def query(self, constraint, sortby=None, typenames=None, maxrecords=10,
              startposition=0):
        """Query records from underlying repository"""

        # run the raw query and get total
        if 'where' in constraint:  # GetRecords with constraint
            LOGGER.debug('constraint detected')
            query = self.session.query(Record)
            query = query.filter(text(constraint['where']))
            query = query.params(self._create_values(constraint['values']))
        else:  # GetRecords sans constraint
            LOGGER.debug('No constraint detected')
            query = self.session.query(Record)
        query = self._apply_ranking(query) if util.ranking_pass else query
        if sortby is not None:
            LOGGER.debug('sorting detected')
            query = self._apply_sorting(
                sortby["propertyname"], sortby["order"],
                sortby.get("spatial", False)
            )

        # always apply limit and offset
        total = self._get_repo_filter(query).count()
        return [str(total), self._get_repo_filter(query).limit(
            maxrecords).offset(startposition).all()]

    def query_ids(self, ids):
        """Query the database with a list of identifiers

        :arg ids: an iterable with the identifiers to be searched
        :type ids: list
        :return:
        :rtype:
        """

        query = self.session.query(Record).filter(
            Record.identifier.in_(ids))
        return self._get_repo_filter(query)

    def query_domain(self, domain, typenames, domainquerytype='list',
                     count=False):
        """Query by property domain values"""
        if domainquerytype == 'range':
            pass
        else:
            if count:
                pass
            else:
                pass

    def query_insert(self, direction="max"):
        """Query to get latest (default) or earliest update to repository"""
        query = self.session.query(Record)
        if direction == "max":
            query = query.order_by(Record.insert_date.asc())
        elif direction == "min":
            query = query.order_by(Record.insert_date.desc())
        return self._get_repo_filter(query).first()

    def query_source(self, source):
        """Query by source"""
        query = self.session.query(Record).filter(
            Record.source == source)
        return self._get_repo_filter(query).all()

    @sqlalchemy_transaction
    def insert_record(self, record):
        """
        Insert a new metadata record into the database.

        :param record: The new record to be added to the database
        :type record: pycsw.core.models.Record
        """

        self.session.add(record)

    @sqlalchemy_transaction
    def update_record(self, record):
        """
        Update database fields for an existing record

        :param record: The updated record that is to be persisted in the
            database
        :type record: pycsw.core.models.Record
        """
        self.session.add(record)

    @sqlalchemy_transaction
    def update_records_with_properties(self, record_properties, constraint):
        rows = 0
        for rpu in record_properties:
            # update queryable column and XML document via XPath
            if 'xpath' not in rpu['rp']:
                self.session.rollback()
                raise RuntimeError('XPath not found for property {}'.format(
                    rpu['rp']['name']))
            if 'dbcol' not in rpu['rp']:
                self.session.rollback()
                raise RuntimeError('property not found for XPath {}'.format(
                    rpu['rp']['name']))
            query = self.query(constraint)
            for record in query:
                attr_name = rpu["rp"]["dbcol"]
                setattr(record, attr_name, rpu["rp"]["dbcol"])
                #record.xml =
                #record.anytext =

    @sqlalchemy_transaction
    def delete_records(self, constraint):
        """Delete records from the repository

        :arg constraint:
        :type constraint:
        :return: The number of records that have been deleted
        :rtype: int
        """
        deleted_count = 0
        possible_parent_ids = []
        for record in self.query(constraint):
            possible_parent_ids.append(record.identifier)
            record.delete()
            deleted_count += 1
        if len(possible_parent_ids) > 0:
            # since we have no real relationships between a record
            # and its parent we have to resort to running another query
            # and try to delete any child records, just in case any of
            # the previously deleted records happenned to be a
            # DatasetSeries
            child_query = self.session.query(Record)
            child_query = child_query.filter(
                Record.parentidentifier.in_(possible_parent_ids))
            for record in child_query:
                record.delete()
                deleted_count += 1
        self.session.commit()
        return deleted_count

    def _get_repo_filter(self, query):
        """Apply repository wide side filter / mask query"""
        return query.filter(self.filter) if self.filter is not None else query

    def _create_values(self, values):
        """Create values suitable for using as parameters to raw SQL queries"""
        value_dict = {}
        for num, value in enumerate(values):
            value_dict['pvalue%d' % num] = value
        return value_dict

    def _apply_ranking(self, query):
        #TODO: Check for dbtype so to extract wkt from postgis native to wkt
        LOGGER.debug('spatial ranking detected')
        LOGGER.debug('Query WKT: %s', util.ranking_query_geometry)
        query = query.order_by(func.get_spatial_overlay_rank(
            Record.wkt_geometry, util.ranking_query_geometry).desc())
        #trying to make this wsgi safe
        util.ranking_pass = False
        util.ranking_query_geometry = ''
        return query

    def _apply_sorting(self, query, property_name, order, spatial_sort):
        """
        Returns a query with the appropriate sorting

        :param property_name:
        :param order:
        :param spatial_sort:
        :return:
        """
        #TODO: Check for dbtype so to extract wkt from postgis native to wkt
        sortby_column = getattr(Record, property_name)

        if order == 'DESC':
            if spatial_sort:
                query = query.order_by(
                    func.get_geometry_area(sortby_column).desc())
            else:
                query = query.order_by(sortby_column.desc())
        else:
            if spatial_sort:
                query = query.order_by(func.get_geometry_area(sortby_column))
            else:
                query = query.order_by(sortby_column)
        return query


