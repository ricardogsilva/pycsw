import logging
from urlparse import urlparse

from .. import util
from ..etree import etree
from .base import MetadataParser


LOGGER = logging.getLogger(__name__)


class WafParser(object):

    def parse(self, url):
        records = []
        raw_content = util.http_request("GET", url)
        parsed_url = urlparse(url)
        try:
            exml = etree.parse(raw_content, parser=etree.HTMLParser())
            LOGGER.debug('collecting links')
            collected_links = []
            for link in exml.xpath('//a/@href'):
                link = link.strip()
                if "?" not in link and link.endswith(".xml"):
                    if link.startswith("/"):
                        # strip path of WAF URL
                        full_link = '{0.scheme}://{0.netloc}{1}'.format(
                            parsed_url, link)
                    else:  # tack on href to WAF URL
                        full_link = '{}/{}'.format(url, link)
                    collected_links.append(full_link)
            LOGGER.debug('{} links found'.format(len(collected_links)))
            for link in collected_links:
                LOGGER.debug('Processing link {}'.format(link))
                raw_link_content = util.http_request('GET', link)
                metadata_parser = MetadataParser()
                records = metadata_parser.parse_description(raw_link_content)
                for record in records:
                    record.source = link
                    record.mdsource = link
        except Exception as err:
            raise RuntimeError('Could not parse WAF: {}'.format(err))
        return records
