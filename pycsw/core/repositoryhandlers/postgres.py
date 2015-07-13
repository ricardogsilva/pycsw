"""
Database handlers for postgresql dialects
"""

import logging

from .base import RepositoryHandler


LOGGER = logging.getLogger(__name__)


class PostgresqlRepositoryHandler(RepositoryHandler):

    def create_plpythonu_functions(self):
        pass

    def create_fts_index(self):
        pass

    def setup_db(self, commit=True):
        super(PostgresqlRepositoryHandler, self).setup_db(commit=False)
        self.create_plpythonu_functions()
        self.create_fts_index()
        self.session.commit()


class PostgisRepositoryHandler(PostgresqlRepositoryHandler):

    def create_geometry_column(self):
        pass

    def setup_db(self, commit=True):
        super(PostgisRepositoryHandler, self).setup_db(commit=False)
        self.create_geometry_column()
        self.session.commit()
