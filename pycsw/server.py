"""Pycsw server module."""

import logging

from .services.factory import get_service

logger = logging.getLogger(__name__)


class PycswServer:
    services = []

    def __init__(self, config_path, **config_keys):
        for service_id, service_config in config_keys.get("services", dict()):
            service = get_service(service_id, service_config)
            self.services.append(service)

    def process_request(self, request):
        raise NotImplementedError


