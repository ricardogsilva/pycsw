import logging

from .. import parameters
from ..operationbase import OperationProcessor

logger = logging.getLogger(__name__)


class GetRecordById202Operation(OperationProcessor):
    name = "GetRecordById"

    id = parameters.TextParameter("Id")
    element_set_name = parameters.TextParameter(
        "ElementSetName", optional=True,
        allowed_values=["brief", "summary", "full"],
        default="brief"
    )
    output_format = parameters.TextParameter("outputFormat", optional=True,
                                             default="application/xml")
    output_schema = parameters.TextParameter(
        "outputSchema",
        optional=True,
        default="http://www.opengis.net/cat/csw/2.02"
    )

    def __init__(self, id=None, element_set_name=None, output_format=None,
                 output_schema=None, enabled=True, allowed_http_verbs=None):
        super().__init__(enabled=enabled,
                         allowed_http_verbs=allowed_http_verbs)
        if id is not None:
            self.id = id
        if element_set_name is not None:
            self.element_set_name = element_set_name
        if output_format is not None:
            self.output_format = output_format
        if output_schema is not None:
            self.output_schema = output_schema
        self.constraints = []

    def __call__(self):
        logger.debug("{0.__class__.__name__} called".format(self))