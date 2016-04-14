import logging

from ..repositorybase import query_translator
from .repository import CswSlaRepository

logger = logging.getLogger(__name__)


@query_translator(CswSlaRepository, "csw:Record")
def translate_csw_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to the csw:Record typename")


@query_translator(CswSlaRepository, "gmd:MD_Metadata")
def translate_csw_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to the gmd:MD_Metadata typename, as coded by a "
          "plugin author")


@query_translator(CswSlaRepository, "rim:SomeType", "rim:AnotherType")
def translate_csw_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to multiple ebRim typenames, as coded by a "
          "plugin author")
