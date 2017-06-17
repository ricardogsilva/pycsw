def parse_wfs(context, repos, record, identifier, version):
    from owslib.wfs import WebFeatureService
    bboxs = []
    recobjs = []
    serviceobj = repos.dataset()

    try:
        md = WebFeatureService(record, version)
    except Exception as err:
        if version == '1.1.0':
            md = WebFeatureService(record, '1.0.0')

    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/wfs')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(
        context,
        serviceobj,
        'pycsw:AnyText',
        util.get_anytext(etree.tostring(md._capabilities))
    )
    _set(context, serviceobj, 'pycsw:Type', 'service')
    _set(context, serviceobj, 'pycsw:Title', md.identification.title)
    _set(context, serviceobj, 'pycsw:Abstract', md.identification.abstract)
    _set(context, serviceobj, 'pycsw:Keywords', ','.join(md.identification.keywords))
    _set(context, serviceobj, 'pycsw:Creator', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:Publisher', md.provider.name)
    _set(context, serviceobj, 'pycsw:Contributor', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:OrganizationName', md.provider.contact.name)
    _set(context, serviceobj, 'pycsw:AccessConstraints', md.identification.accessconstraints)
    _set(context, serviceobj, 'pycsw:OtherConstraints', md.identification.fees)
    _set(context, serviceobj, 'pycsw:Source', record)
    _set(context, serviceobj, 'pycsw:Format', md.identification.type)
    _set(context, serviceobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
    _set(context, serviceobj, 'pycsw:DistanceUOM', 'degrees')
    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:WFS')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:OperatesOn', ','.join(list(md.contents)))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-WFS Web Feature Service,OGC:WFS,%s' % (identifier, md.url)
    ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))

    # generate record foreach featuretype

    LOGGER.info('Harvesting %d WFS featuretypes', len(md.contents))

    for featuretype in md.contents:
        recobj = repos.dataset()
        identifier2 = '%s-%s' % (identifier, md.contents[featuretype].id)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wfs')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'dataset')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        _set(context, recobj, 'pycsw:Title', md.contents[featuretype].title)
        _set(context, recobj, 'pycsw:Abstract', md.contents[featuretype].abstract)
        _set(context, recobj, 'pycsw:Keywords', ','.join(md.contents[featuretype].keywords))

        _set(
            context,
            recobj,
            'pycsw:AnyText',
            util.get_anytext([
                md.contents[featuretype].title,
                md.contents[featuretype].abstract,
                ','.join(md.contents[featuretype].keywords)
            ])
        )

        bbox = md.contents[featuretype].boundingBoxWGS84
        if bbox is not None:
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            wkt_polygon = util.bbox2wktpolygon(tmp)
            _set(context, recobj, 'pycsw:BoundingBox', wkt_polygon)
            _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
            _set(context, recobj, 'pycsw:DistanceUOM', 'degrees')
            bboxs.append(wkt_polygon)

        params = {
            'service': 'WFS',
            'version': '1.1.0',
            'request': 'GetFeature',
            'typename': md.contents[featuretype].id,
        }

        links = [
            '%s,OGC-Web Feature Service,OGC:WFS,%s' % (md.contents[featuretype].id, md.url),
            '%s,File for download,WWW:DOWNLOAD-1.0-http--download,%s' % (md.contents[featuretype].id, build_get_url(md.url, params))
        ]

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))

        recobjs.append(recobj)

    # Derive a bbox based on aggregated featuretype bbox values

    bbox_agg = bbox_from_polygons(bboxs)

    if bbox_agg is not None:
        _set(context, serviceobj, 'pycsw:BoundingBox', bbox_agg)

    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))

    recobjs.insert(0, serviceobj)
    return recobjs
