# TODO - Differentiate between wmts version 1 in the parse() function
def parse_wmts(context, repos, record, identifier):

    from owslib.wmts import WebMapTileService
    recobjs = []
    serviceobj = repos.dataset()

    md = WebMapTileService(record)
    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/wmts/1.0')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(
        context,
        serviceobj,
        'pycsw:AnyText',
        util.get_anytext(md.getServiceXML())
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

    for c in md.contents:
        if md.contents[c].parent is None:
            bbox = md.contents[c].boundingBoxWGS84
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            _set(context, serviceobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
            break
    _set(context, serviceobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
    _set(context, serviceobj, 'pycsw:DistanceUOM', 'degrees')
    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:WMTS')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:OperatesOn', ','.join(list(md.contents)))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-WMTS Web Map Service,OGC:WMTS,%s' % (identifier, md.url),
        ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))
    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))

    recobjs.append(serviceobj)

    # generate record for each layer

    LOGGER.debug('Harvesting %d WMTS layers', len(md.contents))

    for layer in md.contents:
        recobj = repos.dataset()
        keywords = ''
        identifier2 = '%s-%s' % (identifier, md.contents[layer].name)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wmts/1.0')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'dataset')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        if md.contents[layer].title:
            _set(context, recobj, 'pycsw:Title', md.contents[layer].title)
        else:
            _set(context, recobj, 'pycsw:Title', "")
        if md.contents[layer].abstract:
            _set(context, recobj, 'pycsw:Abstract', md.contents[layer].abstract)
        else:
            _set(context, recobj, 'pycsw:Abstract', "")
        if hasattr(md.contents[layer], 'keywords'):  # safeguard against older OWSLib installs
            keywords = ','.join(md.contents[layer].keywords)
        _set(context, recobj, 'pycsw:Keywords', keywords)

        _set(
            context,
            recobj,
            'pycsw:AnyText',
            util.get_anytext([
                md.contents[layer].title,
                md.contents[layer].abstract,
                ','.join(keywords)
            ])
        )

        bbox = md.contents[layer].boundingBoxWGS84

        if bbox is not None:
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
            _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:4326')
            _set(context, recobj, 'pycsw:DistanceUOM', 'degrees')
        else:
            bbox = md.contents[layer].boundingBox
            if bbox:
                tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
                _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
                _set(context, recobj, 'pycsw:CRS', 'urn:ogc:def:crs:EPSG:6.11:%s' % \
                     bbox[-1].split(':')[1])


        params = {
            'service': 'WMTS',
            'version': '1.0.0',
            'request': 'GetTile',
            'layer': md.contents[layer].name,
        }

        links = [
            '%s,OGC-Web Map Tile Service,OGC:WMTS,%s' % (md.contents[layer].name, md.url),
            '%s,Web image thumbnail (URL),WWW:LINK-1.0-http--image-thumbnail,%s' % (md.contents[layer].name, build_get_url(md.url, params))
        ]

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))

        recobjs.append(recobj)

    return recobjs
