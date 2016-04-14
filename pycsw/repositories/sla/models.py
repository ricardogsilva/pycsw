"""Pycsw models for using with the SQLAlchemy repository classes."""

import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Sequence
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
Base = declarative_base()


class Record(Base):
    """Simple database model for pycsw.

    This is a first draft for an SQLAlchemy backend. The single-model approach
    defined here is to be evolved into a more normalized db structure.
    """

    __tablename__ = "records"

    identifier = Column(Text, Sequence("record_id_seq"), primary_key=True)
    title = Column(Text, index=True)
