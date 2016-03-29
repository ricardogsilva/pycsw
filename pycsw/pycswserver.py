"""Pycsw server class.

>>> server = PycswServer(config)
>>> # request is a PycswHttpRequest that was created from the werkzeug request
>>> try:
>>>     service = server.select_service(request)
>>>     operation = service.select_operation(request)
>>>     result = operation.process_request(request)  # ?
>>>     response = service.prepare_response(result)  # ?
>>> except PycswError:
>>>     response = server.generate_error_response()
>>> finally:  # wrap our response as a werkzeug response
>>>     return response

"""

import logging

from . import exceptions
from .services.csw import cswbase
from .services.csw import csw202
from .services.csw.operations import base
from .httprequest import HttpVerb
from . import utilities

logger = logging.getLogger(__name__)


class PycswServer:
    """Processes incoming HTTTP requests."""

    _services = None

    def __init__(self, config_path=None, **config_args):
        # load common config for all services.
        self._services = utilities.ManagedList(manager=self,
                                               related_name="_server")
        csw202_service = self.setup_csw202_service()
        self.services.append(csw202_service)

    @property
    def services(self):
        return self._services

    def setup_csw202_service(self):
        """Create the CSW version 2.0.2 service."""
        csw_schema_processor = cswbase.CswSchemaProcessor(
            namespace="http://www.opengis.net/cat/csw/2.0.2",
            type_names=["csw:Record"],
            record_mapping={
                "title": "dc:title",
                "creator": "dc:creator",
                "subject": "dc:subject",
                "abstract": "dct:abstract",
                "publisher": "dc:publisher",
                "contributor": "dc:contributor",
                "modified": "dct:modified",
                "type_": "dc:type",
                "format_": "dc:format",
                "identifier": "dc:identifier",
                "source": "dc:source",
                "language": "dc:language",
                "association": "dc:relation",
                "bounding_box": "ows:BoundingBox",
                "rights": "dc:rights",
            },
            element_set_names={
                "full": [
                    "dc:identifier",
                    "dc:title",
                    "dc:creator",
                    "dc:subject",
                    "dct:abstract",
                    "dc:publisher",
                    "dc:contributor",
                    "dct:modified",
                    "dc:type",
                    "dc:format",
                    "dc:source",
                    "dc:language",
                    "dc:relation",
                    "ows:BoundingBox",
                    "dc:rights",
                ],
                "summary": [
                    "dc:identifier",
                    "dc:title",
                    "dc:type",
                    "dc:subject",
                    "dc:format",
                    "dc:relation",
                    "dct:modified",
                    "dct:abstract",
                    "dct:spatial",  # ?
                    "ows:BoundingBox",
                ],
                "brief": [
                    "dc:identifier",
                    "dc:title",
                    "dc:type",
                    "ows:BoundingBox",
                ],
            }
        )
        ogc_namespaces = {
            "csw": "http://www.opengis.net/cat/csw/2.0.2",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "ows": "http://www.opengis.net/ows",

        }

        xml_content_type = cswbase.CswContentTypeProcessor(
            media_type="application/xml",
            namespaces=ogc_namespaces,
            schemas=[
                csw_schema_processor,
            ]
        )
        ogc_kvp = cswbase.CswKvpProcessor(
            name="OGC KVP",
            namespaces=ogc_namespaces,
            schemas=[
                csw_schema_processor,
            ]
        )

        get_capabilities = base.GetCapabilities202Operation(
            enabled=True,
        )

        csw202_service = csw202.Csw202Service(
            enabled=True,
            distributed_search=cswbase.CswDistributedSearch(),
            operations=[
                get_capabilities,
            ],
            kvp_types=[
                ogc_kvp,
            ],
            content_types=[
                xml_content_type,
            ]
        )
        return csw202_service

    def select_service(self, request):
        """Get the appropriate service to process the incoming request.

        This method selects the service that is suitable for processing the
        request among the list of currently enabled services.

        Parameters
        ----------
        request: pycsw.httprequest.PycswHttpRequest
            The incoming request object.

        Returns
        -------
        service: pycsw.services.servicebase or None
            The service object that can process the request.

        Raises
        ------
        pycsw.exceptions.PycswError
            If none of the enabled services can process the request.

        """
        for service in (s for s in self.services if s.enabled):
            if service.accepts_request(request):
                # stop on the first suitable service
                return service
        else:
            raise exceptions.PycswError("Could not find a suitable service.")
