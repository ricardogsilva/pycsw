"""
Database handlers for postgresql dialects
"""

import logging

from .base import Repository


LOGGER = logging.getLogger(__name__)


class PostgresqlRepository(Repository):

    def create_plpythonu_functions(self):
        pass

    def create_fts_index(self):
        pass

    def setup_db(self, commit=True):
        super(PostgresqlRepository, self).setup_db(commit=False)
        self.create_plpythonu_functions()
        self.create_fts_index()
        self.session.commit()


class PostgisRepository(PostgresqlRepository):

    def create_geometry_column(self):
        pass

    def setup_db(self, commit=True):
        super(PostgisRepository, self).setup_db(commit=False)
        self.create_geometry_column()
        self.session.commit()
