def parse_waf(context, repos, record, *args, **kwargs):
    recobjs = []
    content = util.http_request('GET', record)
    LOGGER.debug(content)

    try:
        parser = etree.HTMLParser()
        tree = etree.fromstring(content, parser)
    except Exception as err:
        raise Exception('Could not parse WAF: %s' % str(err))

    up = urlparse(record)
    links = []
    LOGGER.info('collecting links')
    for link in tree.xpath('//a/@href'):
        link = link.strip()
        if not link:
            continue
        if link.find('?') != -1:
            continue
        if not link.endswith('.xml'):
            LOGGER.debug('Skipping, not .xml')
            continue
        if '/' in link:  # path is embedded in link
            if link[-1] == '/':  # directory, skip
                continue
            if link[0] == '/':
                # strip path of WAF URL
                link = '%s://%s%s' % (up.scheme, up.netloc, link)
        else:  # tack on href to WAF URL
            link = '%s/%s' % (record, link)
        LOGGER.debug('URL is: %s', link)
        links.append(link)

    LOGGER.debug('%d links found', len(links))
    for link in links:
        LOGGER.info('Processing link %s', link)
        # fetch and parse
        linkcontent = util.http_request('GET', link)
        recobj = _parse_metadata(context, repos, linkcontent)[0]
        recobj.source = link
        recobj.mdsource = link
        recobjs.append(recobj)
    return recobjs
