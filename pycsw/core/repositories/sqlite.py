"""
Database handlers for sqlite dialects
"""

import logging
import os.path

from .base import Repository


LOGGER = logging.getLogger(__name__)


class SqliteRepository(Repository):

    def create_db(self):
        path = self.engine.url.database
        if path != ":memory:":
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                raise RuntimeError("SQLite directory {} does not "
                                   "exist".format(dirname))
        super(SqliteRepository, self).create_db()
