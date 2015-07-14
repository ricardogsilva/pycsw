from . import parameters as params


class ContextModelOperation(object):
    """
    Base class for operations
    """

    name = ""
    method_get = True
    method_post = True
    parameters = []
    constraints = []

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


class GetCapabilitiesOperation(ContextModelOperation):
    name = "GetCapabilities"
    parameters = [params.sections]


class DescribeRecordOperation(ContextModelOperation):
    name = "DescribeRecord"
    parameters = [
        params.schema_language,
        params.typename,
        params.output_format
    ]


class GetRecordsOperation(ContextModelOperation):
    name = 'GetRecords'
    parameters =[
        params.result_type,
        params.typenames,
        params.output_schema,
        params.output_format,
        params.constraint_language,
        params.element_set_name
    ]


class GetRecordByIdOperation(ContextModelOperation):
    name = "GetRecordById"
    parameters = [
        params.output_schema,
        params.output_format,
        params.element_set_name
    ]


class GetRepositoryItemOperation(ContextModelOperation):
    name = "GetRepositoryItem"
    method_post = False


class GetCapabilitiesOperationCsw3(GetCapabilitiesOperation):
    name = "GetCapabilities"
    parameters = [params.sections_csw3, params.accept_versions,
                  params.accept_formats]


class GetRecordsOperationCsw3(ContextModelOperation):
    name = 'GetRecords'
    parameters =[
        params.result_type,
        params.typenames,
        params.output_schema_csw3,
        params.output_format_csw3,
        params.constraint_language,
        params.element_set_name
    ]


class GetRecordByIdOperationCsw3(ContextModelOperation):
    name = "GetRecordById"
    parameters = [
        params.output_schema_csw3,
        params.output_format_csw3,
        params.element_set_name
    ]
