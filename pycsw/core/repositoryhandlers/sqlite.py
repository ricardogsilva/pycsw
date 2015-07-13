"""
Database handlers for sqlite dialects
"""

import logging
import os.path

from .base import RepositoryHandler


LOGGER = logging.getLogger(__name__)


class SqliteRepositoryHandler(RepositoryHandler):

    def create_db(self):
        path = self.engine.url.database
        if path != ":memory:":
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                raise RuntimeError("SQLite directory {} does not "
                                   "exist".format(dirname))
        super(SqliteRepositoryHandler, self).create_db()
