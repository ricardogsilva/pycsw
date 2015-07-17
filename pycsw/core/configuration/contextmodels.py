from . import operations as ops, parameters as params, typenames as types


class ContextModel(object):

    name = ""
    operations = {}
    parameters = {}
    constraints = {}
    typenames = {}

    def __init__(self, name, operations=None, parameters=None,
                 constraints=None, typenames=None):
        self.name = name
        operations = operations or []
        parameters = parameters or []
        constraints = constraints or []
        typenames = typenames or []
        for op in operations:
            self.add_operation(op)
        for param in parameters:
            self.add_parameter(param)
        for constraint in constraints:
            self.add_constraint(constraint)
        for typename in typenames:
            self.add_typename(typename)

    def serialize(self):
        d = {
            "operations": {},
            "parameters": {},
            "constraints": {},
            "typenames": {},
        }
        for op_name, op in self.operations.iteritems():
            d["operations"][op_name] = op.serialize()
        for param_name, param in self.parameters.iteritems():
            d["parameters"][param_name] = {"values": param.values}
        for constraint_name, constraint in self.constraints.iteritems():
            d["constraints"][constraint_name] = {"values": constraint.values}
        for name, typename in self.typenames.iteritems():
            d["typenames"][name] = typename.serialize()
        return d

    def add_operation(self, operation):
        self.operations[operation.name] = operation

    def add_parameter(self, parameter):
        self.parameters[parameter.name] = parameter

    def add_constraint(self, constraint):
        self.parameters[constraint.name] = constraint

    def add_typename(self, typename):
        self.typenames[typename.name] = typename


csw_model = ContextModel(
    "csw",
    operations=[
        ops.get_capabilities,
        ops.describe_record,
        ops.get_records,
        ops.get_record_by_id,
        ops.get_repository_item,
    ],
    parameters=[
        params.version,
        params.service,
    ],
    constraints=[
        params.max_record_default,
        params.post_encoding,
        params.xpath_queryables,
    ],
    typenames=[
        types.csw_typename
    ],
)


csw3_model = ContextModel(
    "csw3",
    operations=[
        ops.get_capabilities_csw3,
        ops.get_records_csw3,
        ops.get_record_by_id_csw3,
        ops.get_repository_item,
    ],
    parameters=[
        params.version,
        params.service,
    ],
    constraints=[
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
    ],
    typenames=[
        types.csw3_typename
    ],
)
