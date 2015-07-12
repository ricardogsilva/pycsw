"""
Handlers for interacting with sqlalchemy's orm in order to perform database
related instructions
"""

import os.path

from . import models


def db_handler_factory(engine, session):
    """
    Return the appropriate handler for dealing with the input engine.

    :param engine:
    :param session:
    :return:
    """

    if engine.dialect.name == "sqlite":
        handler_class = SqliteDatabaseHandler
    elif engine.dialect.name == "postgresql":
        postgis_lib_version = None
        for row in session.execute('select(postgis_lib_version())'):
            postgis_lib_version = row[0]
        if postgis_lib_version is not None:
            handler_class = PostgisDatabaseHandler
        else:
            handler_class = PostgresqlDatabaseHandler
    else:
        handler_class = DatabaseHandler
    return handler_class()


class DatabaseHandler(object):
    engine = None
    session = None

    def __init__(self, engine, session):
        """Base implementation for dealing with database operations"""
        self.engine = engine
        self.session = session

    def create_db(self):
        # the create_all method will not attempt to recreate tables
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
            f_table_name=models.Record.__tablename__,
            f_geometry_column="wkt_geometry",
            geometry_type=3, coord_dimension=2, srid=4326,
            geometry_format="WKT"
        )
        self.session.add(record)

    def setup_db(self, commit=True):
        self.create_db()
        self.populate_spatial_ref_sys()
        self.populate_geometry_columns()
        self.session.commit()


class SqliteDatabaseHandler(DatabaseHandler):

    def create_db(self):
        path = self.engine.url.database
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            raise RuntimeError("SQLite directory {} does not "
                               "exist".format(dirname))
        super(SqliteDatabaseHandler, self).setup_db()


class PostgresqlDatabaseHandler(DatabaseHandler):

    def create_plpythonu_functions(self):
        pass

    def create_fts_index(self):
        pass

    def setup_db(self, commit=True):
        super(PostgresqlDatabaseHandler, self).setup_db(commit=False)
        self.create_plpythonu_functions()
        self.create_fts_index()
        self.session.commit()


class PostgisDatabaseHandler(PostgresqlDatabaseHandler):

    def create_geometry_column(self):
        pass

    def setup_db(self, commit=True):
        super(PostgisDatabaseHandler, self).setup_db(commit=False)
        self.create_geometry_column()
        self.session.commit()
