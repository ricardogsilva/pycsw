def _parse_iso(context, repos, exml):

    from owslib.iso import MD_Metadata

    recobj = repos.dataset()
    links = []

    md = MD_Metadata(exml)

    _set(context, recobj, 'pycsw:Identifier', md.identifier)
    _set(context, recobj, 'pycsw:Typename', 'gmd:MD_Metadata')
    _set(context, recobj, 'pycsw:Schema', context.namespaces['gmd'])
    _set(context, recobj, 'pycsw:MdSource', 'local')
    _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(context, recobj, 'pycsw:XML', md.xml)
    _set(context, recobj, 'pycsw:AnyText', util.get_anytext(exml))
    _set(context, recobj, 'pycsw:Language', md.language)
    _set(context, recobj, 'pycsw:Type', md.hierarchy)
    _set(context, recobj, 'pycsw:ParentIdentifier', md.parentidentifier)
    _set(context, recobj, 'pycsw:Date', md.datestamp)
    _set(context, recobj, 'pycsw:Modified', md.datestamp)
    _set(context, recobj, 'pycsw:Source', md.dataseturi)
    if md.referencesystem is not None:
        _set(context, recobj, 'pycsw:CRS','urn:ogc:def:crs:EPSG:6.11:%s' %
             md.referencesystem.code)

    if hasattr(md, 'identification'):
        _set(context, recobj, 'pycsw:Title', md.identification.title)
        _set(context, recobj, 'pycsw:AlternateTitle', md.identification.alternatetitle)
        _set(context, recobj, 'pycsw:Abstract', md.identification.abstract)
        _set(context, recobj, 'pycsw:Relation', md.identification.aggregationinfo)

        if hasattr(md.identification, 'temporalextent_start'):
            _set(context, recobj, 'pycsw:TempExtent_begin', md.identification.temporalextent_start)
        if hasattr(md.identification, 'temporalextent_end'):
            _set(context, recobj, 'pycsw:TempExtent_end', md.identification.temporalextent_end)

        if len(md.identification.topiccategory) > 0:
            _set(context, recobj, 'pycsw:TopicCategory', md.identification.topiccategory[0])

        if len(md.identification.resourcelanguage) > 0:
            _set(context, recobj, 'pycsw:ResourceLanguage', md.identification.resourcelanguage[0])

        if hasattr(md.identification, 'bbox'):
            bbox = md.identification.bbox
        else:
            bbox = None

        if (hasattr(md.identification, 'keywords') and
                    len(md.identification.keywords) > 0):
            all_keywords = [item for sublist in md.identification.keywords for item in sublist['keywords'] if item is not None]
            _set(context, recobj, 'pycsw:Keywords', ','.join(all_keywords))
            _set(context, recobj, 'pycsw:KeywordType', md.identification.keywords[0]['type'])

        if (hasattr(md.identification, 'creator') and
                    len(md.identification.creator) > 0):
            all_orgs = set([item.organization for item in md.identification.creator if hasattr(item, 'organization') and item.organization is not None])
            _set(context, recobj, 'pycsw:Creator', ';'.join(all_orgs))
        if (hasattr(md.identification, 'publisher') and
                    len(md.identification.publisher) > 0):
            all_orgs = set([item.organization for item in md.identification.publisher if hasattr(item, 'organization') and item.organization is not None])
            _set(context, recobj, 'pycsw:Publisher', ';'.join(all_orgs))
        if (hasattr(md.identification, 'contributor') and
                    len(md.identification.contributor) > 0):
            all_orgs = set([item.organization for item in md.identification.contributor if hasattr(item, 'organization') and item.organization is not None])
            _set(context, recobj, 'pycsw:Contributor', ';'.join(all_orgs))

        if (hasattr(md.identification, 'contact') and
                    len(md.identification.contact) > 0):
            all_orgs = set([item.organization for item in md.identification.contact if hasattr(item, 'organization') and item.organization is not None])
            _set(context, recobj, 'pycsw:OrganizationName', ';'.join(all_orgs))

        if len(md.identification.securityconstraints) > 0:
            _set(context, recobj, 'pycsw:SecurityConstraints',
                 md.identification.securityconstraints[0])
        if len(md.identification.accessconstraints) > 0:
            _set(context, recobj, 'pycsw:AccessConstraints',
                 md.identification.accessconstraints[0])
        if len(md.identification.otherconstraints) > 0:
            _set(context, recobj, 'pycsw:OtherConstraints', md.identification.otherconstraints[0])

        if hasattr(md.identification, 'date'):
            for datenode in md.identification.date:
                if datenode.type == 'revision':
                    _set(context, recobj, 'pycsw:RevisionDate', datenode.date)
                elif datenode.type == 'creation':
                    _set(context, recobj, 'pycsw:CreationDate', datenode.date)
                elif datenode.type == 'publication':
                    _set(context, recobj, 'pycsw:PublicationDate', datenode.date)

        if hasattr(md.identification, 'extent') and hasattr(md.identification.extent, 'description_code'):
            _set(context, recobj, 'pycsw:GeographicDescriptionCode', md.identification.extent.description_code)

        if len(md.identification.denominators) > 0:
            _set(context, recobj, 'pycsw:Denominator', md.identification.denominators[0])
        if len(md.identification.distance) > 0:
            _set(context, recobj, 'pycsw:DistanceValue', md.identification.distance[0])
        if len(md.identification.uom) > 0:
            _set(context, recobj, 'pycsw:DistanceUOM', md.identification.uom[0])

        if len(md.identification.classification) > 0:
            _set(context, recobj, 'pycsw:Classification', md.identification.classification[0])
        if len(md.identification.uselimitation) > 0:
            _set(context, recobj, 'pycsw:ConditionApplyingToAccessAndUse',
                 md.identification.uselimitation[0])

    if hasattr(md.identification, 'format'):
        _set(context, recobj, 'pycsw:Format', md.distribution.format)

    if md.serviceidentification is not None:
        _set(context, recobj, 'pycsw:ServiceType', md.serviceidentification.type)
        _set(context, recobj, 'pycsw:ServiceTypeVersion', md.serviceidentification.version)

        _set(context, recobj, 'pycsw:CouplingType', md.serviceidentification.couplingtype)

    service_types = []
    for smd in md.identificationinfo:
        if smd.identtype == 'service' and smd.type is not None:
            service_types.append(smd.type)

    _set(context, recobj, 'pycsw:ServiceType', ','.join(service_types))

    #if len(md.serviceidentification.operateson) > 0:
    #    _set(context, recobj, 'pycsw:operateson = VARCHAR(32),
    #_set(context, recobj, 'pycsw:operation VARCHAR(32),
    #_set(context, recobj, 'pycsw:operatesonidentifier VARCHAR(32),
    #_set(context, recobj, 'pycsw:operatesoname VARCHAR(32),


    if hasattr(md.identification, 'dataquality'):
        _set(context, recobj, 'pycsw:Degree', md.dataquality.conformancedegree)
        _set(context, recobj, 'pycsw:Lineage', md.dataquality.lineage)
        _set(context, recobj, 'pycsw:SpecificationTitle', md.dataquality.specificationtitle)
        if hasattr(md.dataquality, 'specificationdate'):
            _set(context, recobj, 'pycsw:specificationDate',
                 md.dataquality.specificationdate[0].date)
            _set(context, recobj, 'pycsw:SpecificationDateType',
                 md.dataquality.specificationdate[0].datetype)

    if hasattr(md, 'contact') and len(md.contact) > 0:
        _set(context, recobj, 'pycsw:ResponsiblePartyRole', md.contact[0].role)

    LOGGER.info('Scanning for links')
    if hasattr(md, 'distribution'):
        dist_links = []
        if hasattr(md.distribution, 'online'):
            LOGGER.debug('Scanning for gmd:transferOptions element(s)')
            dist_links.extend(md.distribution.online)
        if hasattr(md.distribution, 'distributor'):
            LOGGER.debug('Scanning for gmd:distributorTransferOptions element(s)')
            for dist_member in md.distribution.distributor:
                dist_links.extend(dist_member.online)
        for link in dist_links:
            if link.url is not None and link.protocol is None:  # take a best guess
                link.protocol = sniff_link(link.url)
            linkstr = '%s,%s,%s,%s' % \
                      (link.name, link.description, link.protocol, link.url)
            links.append(linkstr)

    try:
        LOGGER.debug('Scanning for srv:SV_ServiceIdentification links')
        for sident in md.identificationinfo:
            if hasattr(sident, 'operations'):
                for sops in sident.operations:
                    for scpt in sops['connectpoint']:
                        LOGGER.debug('adding srv link %s', scpt.url)
                        linkstr = '%s,%s,%s,%s' % \
                                  (scpt.name, scpt.description, scpt.protocol, scpt.url)
                        links.append(linkstr)
    except Exception as err:  # srv: identification does not exist
        LOGGER.exception('no srv:SV_ServiceIdentification links found')

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
