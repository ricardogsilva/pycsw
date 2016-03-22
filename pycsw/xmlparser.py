"""A custom XML parser for pycsw

This parser includes safer defaults, in order to protect from potential
attacks.

"""

from lxml import etree


def get_parser(encoding="utf-8", schema_path=None):
    """A factory for generating safe lxml parsers."""

    schema = etree.XMLSchema(file=schema_path) if schema_path else None
    parser = etree.XMLParser(encoding=encoding, resolve_entities=False,
                             XMLSchema_schema=schema)
    return parser
