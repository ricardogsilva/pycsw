"""Csw SQLALchemy base classes.

The following is a draft of a potential interactive session with the code,
serving more as a reminder for this intial dev stage than as any guidance for
a future API:

>>> from uuid import uuid1
>>> from sqlalchemy import create_engine
>>> from sqlalchemy.orm import sessionmaker
>>> from pycsw.repositories.sla.models import Record
>>> engine = create_engine("sqlite:///:memory:", echo=True)
>>> Session = sessionmaker()
>>> Session.configure(bind=engine)
>>> this_session = Session()
>>> sla_repo = CswSlaRepository(engine, this_session)
>>> sla_repo.create_db()
>>> record1 = Record(identifier=str(uuid1(), title="My phony csw record")
>>> record2 = Record(identifier=str(uuid1(), title="Another phony csw record")
>>> record3 = Record(identifier=str(uuid1(), title="One more phony csw record")
>>> sla_repo.session.add(record1)
>>> sla_repo.session.add(record2)
>>> sla_repo.session.add(record3)
>>> sla_repo.session.commit()

"""


import logging

from ... import exceptions
from ..repositorybase import CswRepository
from .models import Base
from .models import Record


logger = logging.getLogger(__name__)


class CswSlaRepository(CswRepository):
    """SQLAlchemy base repository class."""

    _query_translators = {}
    engine = None
    session = None

    def __init__(self, engine, session):
        super().__init__()
        self.engine = engine
        self.session = session

    def create_db(self):
        path = self.engine.url.database
        if self.engine.url.database != ":memory:":
            raise exceptions.PycswError("Non memory based databases are not "
                                        "supported yet")
        Base.metadata.create_all(self.engine)

    def get_record_by_id(self, id):
        return self.session.query(Record).first()


