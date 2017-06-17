# TODO - Differentiate between wps 1 and other versions the parse() function
def parse_wps(context, repos, record, identifier):

    from owslib.wps import WebProcessingService
    recobjs = []
    serviceobj = repos.dataset()

    md = WebProcessingService(record)

    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', 'http://www.opengis.net/wps/1.0.0')
    _set(context, serviceobj, 'pycsw:MdSource', record)
    _set(context, serviceobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(
        context,
        serviceobj,
        'pycsw:AnyText',
        util.get_anytext(md._capabilities)
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

    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:WPS')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:OperatesOn', ','.join([o.identifier for o in md.processes]))
    _set(context, serviceobj, 'pycsw:CouplingType', 'loose')

    links = [
        '%s,OGC-WPS Web Processing Service,OGC:WPS,%s' % (identifier, md.url),
        '%s,OGC-WPS Capabilities service (ver 1.0.0),OGC:WPS-1.1.0-http-get-capabilities,%s' % (identifier, build_get_url(md.url, {'service': 'WPS', 'version': '1.0.0', 'request': 'GetCapabilities'})),
        ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))
    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))

    recobjs.append(serviceobj)

    # generate record foreach process

    LOGGER.info('Harvesting %d WPS processes', len(md.processes))

    for process in md.processes:
        recobj = repos.dataset()
        identifier2 = '%s-%s' % (identifier, process.identifier)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', 'http://www.opengis.net/wps/1.0.0')
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'software')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        _set(context, recobj, 'pycsw:Title', process.title)
        _set(context, recobj, 'pycsw:Abstract', process.abstract)

        _set(
            context,
            recobj,
            'pycsw:AnyText',
            util.get_anytext([process.title, process.abstract])
        )

        params = {
            'service': 'WPS',
            'version': '1.0.0',
            'request': 'DescribeProcess',
            'identifier': process.identifier
        }

        links.append(
            '%s,OGC-WPS DescribeProcess service (ver 1.0.0),OGC:WPS-1.0.0-http-describe-process,%s' % (identifier, build_get_url(md.url, {'service': 'WPS', 'version': '1.0.0', 'request': 'DescribeProcess', 'identifier': process.identifier})))

        _set(context, recobj, 'pycsw:Links', '^'.join(links))
        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))

        recobjs.append(recobj)

    return recobjs
