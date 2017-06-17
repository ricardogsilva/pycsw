def parse_fgdc(context, repos, exml):

    from owslib.fgdc import Metadata

    recobj = repos.dataset()
    links = []

    md = Metadata(exml)

    if md.idinfo.datasetid is not None:  # we need an identifier
        _set(context, recobj, 'pycsw:Identifier', md.idinfo.datasetid)
    else:  # generate one ourselves
        _set(context, recobj, 'pycsw:Identifier', uuid.uuid1().urn)

    _set(context, recobj, 'pycsw:Typename', 'fgdc:metadata')
    _set(context, recobj, 'pycsw:Schema', context.namespaces['fgdc'])
    _set(context, recobj, 'pycsw:MdSource', 'local')
    _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(context, recobj, 'pycsw:XML', md.xml)
    _set(context, recobj, 'pycsw:AnyText', util.get_anytext(exml))
    _set(context, recobj, 'pycsw:Language', 'en-US')

    if hasattr(md.idinfo, 'descript'):
        _set(context, recobj, 'pycsw:Abstract', md.idinfo.descript.abstract)

    if hasattr(md.idinfo, 'keywords'):
        if md.idinfo.keywords.theme:
            _set(context, recobj, 'pycsw:Keywords', \
                 ','.join(md.idinfo.keywords.theme[0]['themekey']))

    if hasattr(md.idinfo.timeperd, 'timeinfo'):
        if hasattr(md.idinfo.timeperd.timeinfo, 'rngdates'):
            _set(context, recobj, 'pycsw:TempExtent_begin',
                 md.idinfo.timeperd.timeinfo.rngdates.begdate)
            _set(context, recobj, 'pycsw:TempExtent_end',
                 md.idinfo.timeperd.timeinfo.rngdates.enddate)

    if hasattr(md.idinfo, 'origin'):
        _set(context, recobj, 'pycsw:Creator', md.idinfo.origin)
        _set(context, recobj, 'pycsw:Publisher',  md.idinfo.origin)
        _set(context, recobj, 'pycsw:Contributor', md.idinfo.origin)

    if hasattr(md.idinfo, 'ptcontac'):
        _set(context, recobj, 'pycsw:OrganizationName', md.idinfo.ptcontac.cntorg)
    _set(context, recobj, 'pycsw:AccessConstraints', md.idinfo.accconst)
    _set(context, recobj, 'pycsw:OtherConstraints', md.idinfo.useconst)
    _set(context, recobj, 'pycsw:Date', md.metainfo.metd)

    if hasattr(md.idinfo, 'spdom') and hasattr(md.idinfo.spdom, 'bbox'):
        bbox = md.idinfo.spdom.bbox
    else:
        bbox = None

    if hasattr(md.idinfo, 'citation'):
        if hasattr(md.idinfo.citation, 'citeinfo'):
            _set(context, recobj, 'pycsw:Type',  md.idinfo.citation.citeinfo['geoform'])
            _set(context, recobj, 'pycsw:Title', md.idinfo.citation.citeinfo['title'])
            _set(context, recobj,
                 'pycsw:PublicationDate', md.idinfo.citation.citeinfo['pubdate'])
            _set(context, recobj, 'pycsw:Format', md.idinfo.citation.citeinfo['geoform'])
            if md.idinfo.citation.citeinfo['onlink']:
                for link in md.idinfo.citation.citeinfo['onlink']:
                    tmp = ',,,%s' % link
                    links.append(tmp)

    if hasattr(md, 'distinfo') and hasattr(md.distinfo, 'stdorder'):
        for link in md.distinfo.stdorder['digform']:
            tmp = ',%s,,%s' % (link['name'], link['url'])
            links.append(tmp)

    if len(links) > 0:
        _set(context, recobj, 'pycsw:Links', '^'.join(links))

    if bbox is not None:
        try:
            tmp = '%s,%s,%s,%s' % (bbox.minx, bbox.miny, bbox.maxx, bbox.maxy)
            _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
        except:  # coordinates are corrupted, do not include
            _set(context, recobj, 'pycsw:BoundingBox', None)
    else:
        _set(context, recobj, 'pycsw:BoundingBox', None)

    return recobj
