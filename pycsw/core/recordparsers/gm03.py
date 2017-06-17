def _parse_gm03(context, repos, exml):

    def get_value_by_language(pt_group, language, pt_type='text'):
        for ptg in pt_group:
            if ptg.language == language:
                if pt_type == 'url':
                    val = ptg.plain_url
                else:  # 'text'
                    val = ptg.plain_text
                return val

    from owslib.gm03 import GM03

    recobj = repos.dataset()
    links = []

    md = GM03(exml)

    if hasattr(md.data, 'core'):
        data = md.data.core
    elif hasattr(md.data, 'comprehensive'):
        data = md.data.comprehensive

    language = data.metadata.language

    _set(context, recobj, 'pycsw:Identifier', data.metadata.file_identifier)
    _set(context, recobj, 'pycsw:Typename', 'gm03:TRANSFER')
    _set(context, recobj, 'pycsw:Schema', context.namespaces['gm03'])
    _set(context, recobj, 'pycsw:MdSource', 'local')
    _set(context, recobj, 'pycsw:InsertDate', util.get_today_and_now())
    _set(context, recobj, 'pycsw:XML', md.xml)
    _set(context, recobj, 'pycsw:AnyText', util.get_anytext(exml))
    _set(context, recobj, 'pycsw:Language', data.metadata.language)
    _set(context, recobj, 'pycsw:Type', data.metadata.hierarchy_level[0])
    _set(context, recobj, 'pycsw:Date', data.metadata.date_stamp)

    for dt in data.date:
        if dt.date_type == 'modified':
            _set(context, recobj, 'pycsw:Modified', dt.date)
        elif dt.date_type == 'creation':
            _set(context, recobj, 'pycsw:CreationDate', dt.date)
        elif dt.date_type == 'publication':
            _set(context, recobj, 'pycsw:PublicationDate', dt.date)
        elif dt.date_type == 'revision':
            _set(context, recobj, 'pycsw:RevisionDate', dt.date)

    if hasattr(data, 'metadata_point_of_contact'):
        _set(context, recobj, 'pycsw:ResponsiblePartyRole', data.metadata_point_of_contact.role)

    _set(context, recobj, 'pycsw:Source', data.metadata.dataset_uri)
    _set(context, recobj, 'pycsw:CRS','urn:ogc:def:crs:EPSG:6.11:4326')

    if hasattr(data, 'citation'):
        _set(context, recobj, 'pycsw:Title', get_value_by_language(data.citation.title.pt_group, language))

    if hasattr(data, 'data_identification'):
        _set(context, recobj, 'pycsw:Abstract', get_value_by_language(data.data_identification.abstract.pt_group, language))
        if hasattr(data.data_identification, 'topic_category'):
            _set(context, recobj, 'pycsw:TopicCategory', data.data_identification.topic_category)
        _set(context, recobj, 'pycsw:ResourceLanguage', data.data_identification.language)

    if hasattr(data, 'format'):
        _set(context, recobj, 'pycsw:Format', data.format.name)

    # bbox
    if hasattr(data, 'geographic_bounding_box'):
        try:
            tmp = '%s,%s,%s,%s' % (data.geographic_bounding_box.west_bound_longitude,
                                   data.geographic_bounding_box.south_bound_latitude,
                                   data.geographic_bounding_box.east_bound_longitude,
                                   data.geographic_bounding_box.north_bound_latitude)
            _set(context, recobj, 'pycsw:BoundingBox', util.bbox2wktpolygon(tmp))
        except:  # coordinates are corrupted, do not include
            _set(context, recobj, 'pycsw:BoundingBox', None)
    else:
        _set(context, recobj, 'pycsw:BoundingBox', None)

    # temporal extent
    if hasattr(data, 'temporal_extent'):
        if data.temporal_extent.extent['begin'] is not None and data.temporal_extent.extent['end'] is not None:
            _set(context, recobj, 'pycsw:TempExtent_begin', data.temporal_extent.extent['begin'])
            _set(context, recobj, 'pycsw:TempExtent_end', data.temporal_extent.extent['end'])

    # online linkages
    name = description = protocol = ''

    if hasattr(data, 'online_resource'):
        if hasattr(data.online_resource, 'name'):
            name = get_value_by_language(data.online_resource.name.pt_group, language)
        if hasattr(data.online_resource, 'description'):
            description = get_value_by_language(data.online_resource.description.pt_group, language)
        linkage = get_value_by_language(data.online_resource.linkage.pt_group, language, 'url')

        tmp = '%s,"%s",%s,%s' % (name, description, protocol, linkage)
        links.append(tmp)

    if len(links) > 0:
        _set(context, recobj, 'pycsw:Links', '^'.join(links))

    keywords = []
    for kw in data.keywords:
        keywords.append(get_value_by_language(kw.keyword.pt_group, language))
        _set(context, recobj, 'pycsw:Keywords', ','.join(keywords))

    # contacts
    return recobj
