"""
Factory functions for creating database handler classes.
"""

import logging

from .base import RepositoryHandler
from .sqlite import SqliteRepositoryHandler
from .postgres import PostgresqlRepositoryHandler, PostgisRepositoryHandler


LOGGER = logging.getLogger(__name__)


def get_repository_handler(engine, session):
    """
    Return the appropriate handler for dealing with the input engine.

    If the input engine specifies a postgresql dialect, we inspect the
    database in order to determine if PostGIS is available.

    :param engine:
    :param session:
    :return:
    """

    if engine.dialect.name == "sqlite":
        handler_class = SqliteRepositoryHandler
    elif engine.dialect.name == "postgresql":
        postgis_lib_version = None
        for row in session.execute('select(postgis_lib_version())'):
            postgis_lib_version = row[0]
        if postgis_lib_version is not None:
            handler_class = PostgisRepositoryHandler
        else:
            handler_class = PostgresqlRepositoryHandler
    else:
        handler_class = RepositoryHandler
    LOGGER.debug("handler_class: {}".format(handler_class))
    return handler_class(engine, session)


