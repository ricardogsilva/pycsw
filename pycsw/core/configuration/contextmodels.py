from . import operations as ops, parameters as params, typenames as types


class ContextModel(object):

    name = ""
    operations = []
    parameters = []
    constraints = []
    typenames = []

    def serialize(self):
        d = {
            "operations": {},
            "parameters": {},
            "constraints": {},
            "typenames": {},
        }
        for op in self.operations:
            d["operations"][op.name] = op.serialize()
        for p in self.parameters:
            d["parameters"][p.name] = {"values": p.values}
        for c in self.constraints:
            d["constraints"][c.name] = {"values": c.values}
        for t in self.typenames:
            d["typenames"][t.name] = t.serialize()
        return d


class CswContextModel(ContextModel):
    name = "csw"
    operations = [
        ops.GetCapabilitiesOperation(),
        ops.DescribeRecordOperation(),
        ops.GetRecordsOperation(),
        ops.GetRecordByIdOperation(),
        ops.GetRepositoryItemOperation(),
    ]
    parameters = [
        params.version,
        params.service
    ]
    constraints = [
        params.max_record_default,
        params.post_encoding,
        params.xpath_queryables
    ]
    typenames = [
        types.csw_typename,
    ]


class Csw3ContextModel(ContextModel):
    name = "csw3"
    operations = [
        ops.GetCapabilitiesOperationCsw3(),
        ops.GetRecordsOperationCsw3(),
        ops.GetRecordByIdOperationCsw3(),
        ops.GetRepositoryItemOperation(),
    ]
    parameters = [
        params.version,
        params.service
    ]
    constraints = [
        params.max_record_default,
        params.post_encoding,
        params.xpath_queryables,
        params.open_search,
        params.get_capabilities_xml,
        params.get_record_by_id_xml,
        params.get_records_basic_xml,
        params.get_records_distributed_xml,
        params.get_records_distributed_kvp,
        params.get_records_async_xml,
        params.get_records_async_kvp,
        params.get_domain_xml,
        params.get_domain_kvp,
        params.transaction,
        params.harvest_basic_xml,
        params.harvest_basic_kvp,
        params.harvest_async_xml,
        params.harvest_async_kvp,
        params.harvest_periodic_xml,
        params.harvest_periodic_kvp,
        params.filter_cql,
        params.filter_fes_xml,
        params.filter_fes_kvp_advanced,
        params.supported_gml_versions,
        params.default_sorting_algorithm,
        params.core_queryables,
        params.core_sortables,
    ]
    typenames = [
        types.csw3_typename,
    ]



