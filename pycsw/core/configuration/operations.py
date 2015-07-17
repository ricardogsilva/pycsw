from . import parameters as params


class ContextModelOperation(object):
    """
    Base class for operations
    """

    name = ""
    method_get = True
    method_post = True
    parameters = {}
    constraints = {}

    def __init__(self, name, method_get=True, method_post=True,
                 parameters=None, constraints=None):
        self.name = name
        self.method_get = method_get
        self.method_post = method_post
        parameters = parameters or []
        constraints = constraints or []
        for p in parameters:
            self.parameters[p.name] = p
        for c in constraints:
            self.constraints[c.name] = c

    def serialize(self):
        d = {
            "methods": {
                "get": self.method_get,
                "post": self.method_post,
            },
            "parameters": {},
        }
        for p in self.parameters:
            d["parameters"][p.name] = {"values": p.values}


get_capabilities = ContextModelOperation(
    "GetCapabilities",
    parameters=[
        params.sections
    ],
)


get_capabilities_csw3 = ContextModelOperation(
    "GetCapabilities",
    parameters=[
        params.sections_csw3,
        params.accept_versions,
        params.accept_formats,
    ]
)


describe_record = ContextModelOperation(
    "DescribeRecord",
    parameters=[
        params.schema_language,
        params.typename,
        params.output_format,
    ]
)


get_records = ContextModelOperation(
    "GetRecords",
    parameters=[
        params.result_type,
        params.typenames,
        params.output_schema,
        params.output_format,
        params.constraint_language,
        params.element_set_name,
    ]
)

get_records_csw3 = ContextModelOperation(
    "GetRecords",
    parameters=[
        params.result_type,
        params.typenames,
        params.output_schema_csw3,
        params.output_format_csw3,
        params.constraint_language,
        params.element_set_name
    ]
)


get_record_by_id = ContextModelOperation(
    "GetRecordById",
    parameters=[
        params.output_schema,
        params.output_format,
        params.element_set_name
    ]
)


get_record_by_id_csw3 = ContextModelOperation(
    "GetRecordById",
    parameters=[
        params.output_schema_csw3,
        params.output_format_csw3,
        params.element_set_name
    ]
)


get_repository_item = ContextModelOperation(
    "GetRepositoryItem",
    method_post=False,
)
