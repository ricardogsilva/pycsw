def parse_sos(context, repos, record, identifier, version):

    from owslib.sos import SensorObservationService

    bboxs = []
    recobjs = []
    serviceobj = repos.dataset()

    if version == '1.0.0':
        schema = 'http://www.opengis.net/sos/1.0'
    else:
        schema = 'http://www.opengis.net/sos/2.0'

    md = SensorObservationService(record, version=version)

    # generate record of service instance
    _set(context, serviceobj, 'pycsw:Identifier', identifier)
    _set(context, serviceobj, 'pycsw:Typename', 'csw:Record')
    _set(context, serviceobj, 'pycsw:Schema', schema)
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
    _set(context, serviceobj, 'pycsw:ServiceType', 'OGC:SOS')
    _set(context, serviceobj, 'pycsw:ServiceTypeVersion', md.identification.version)
    _set(context, serviceobj, 'pycsw:Operation', ','.join([d.name for d in md.operations]))
    _set(context, serviceobj, 'pycsw:OperatesOn', ','.join(list(md.contents)))
    _set(context, serviceobj, 'pycsw:CouplingType', 'tight')

    links = [
        '%s,OGC-SOS Sensor Observation Service,OGC:SOS,%s' % (identifier, md.url),
        ]

    _set(context, serviceobj, 'pycsw:Links', '^'.join(links))

    # generate record foreach offering

    LOGGER.info('Harvesting %d SOS ObservationOffering\'s ', len(md.contents))

    for offering in md.contents:
        recobj = repos.dataset()
        identifier2 = '%s-%s' % (identifier, md.contents[offering].id)
        _set(context, recobj, 'pycsw:Identifier', identifier2)
        _set(context, recobj, 'pycsw:Typename', 'csw:Record')
        _set(context, recobj, 'pycsw:Schema', schema)
        _set(context, recobj, 'pycsw:MdSource', record)
        _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
        _set(context, recobj, 'pycsw:Type', 'dataset')
        _set(context, recobj, 'pycsw:ParentIdentifier', identifier)
        _set(context, recobj, 'pycsw:Title', md.contents[offering].description)
        _set(context, recobj, 'pycsw:Abstract', md.contents[offering].description)
        begin = md.contents[offering].begin_position
        end = md.contents[offering].end_position
        _set(context, recobj, 'pycsw:TempExtent_begin',
             util.datetime2iso8601(begin) if begin is not None else None)
        _set(context, recobj, 'pycsw:TempExtent_end',
             util.datetime2iso8601(end) if end is not None else None)

        #For observed_properties that have mmi url or urn, we simply want the observation name.
        observed_properties = []
        for obs in md.contents[offering].observed_properties:
            #Observation is stored as urn representation: urn:ogc:def:phenomenon:mmisw.org:cf:sea_water_salinity
            if obs.lower().startswith(('urn:', 'x-urn')):
                observed_properties.append(obs.rsplit(':', 1)[-1])
            #Observation is stored as uri representation: http://mmisw.org/ont/cf/parameter/sea_floor_depth_below_sea_surface
            elif obs.lower().startswith(('http://', 'https://')):
                observed_properties.append(obs.rsplit('/', 1)[-1])
            else:
                observed_properties.append(obs)
        #Build anytext from description and the observed_properties.
        anytext = []
        anytext.append(md.contents[offering].description)
        anytext.extend(observed_properties)
        _set(context, recobj, 'pycsw:AnyText', util.get_anytext(anytext))
        _set(context, recobj, 'pycsw:Keywords', ','.join(observed_properties))

        bbox = md.contents[offering].bbox
        if bbox is not None:
            tmp = '%s,%s,%s,%s' % (bbox[0], bbox[1], bbox[2], bbox[3])
            wkt_polygon = util.bbox2wktpolygon(tmp)
            _set(context, recobj, 'pycsw:BoundingBox', wkt_polygon)
            _set(context, recobj, 'pycsw:CRS', md.contents[offering].bbox_srs.id)
            _set(context, recobj, 'pycsw:DistanceUOM', 'degrees')
            bboxs.append(wkt_polygon)

        _set(context, recobj, 'pycsw:XML', base.caps2iso(recobj, md, context))
        recobjs.append(recobj)

    # Derive a bbox based on aggregated featuretype bbox values

    bbox_agg = bbox_from_polygons(bboxs)

    if bbox_agg is not None:
        _set(context, serviceobj, 'pycsw:BoundingBox', bbox_agg)

    _set(context, serviceobj, 'pycsw:XML', base.caps2iso(serviceobj, md, context))
    recobjs.insert(0, serviceobj)

    return recobjs
