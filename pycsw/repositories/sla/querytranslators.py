import logging

logger = logging.getLogger(__name__)


def translate_csw_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to the csw:Record typename")


def translate_gmd_md_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to the gmd:MD_Metadata typename, as coded by a "
          "plugin author")


def translate_ebrim_record(query):
    print("I'd translate the input query to the CswSlaRepository known "
          "fields according to multiple ebRim typenames, as coded by a "
          "plugin author")
