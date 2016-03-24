from unittest import mock

import pytest

from pycsw.services import factory
from pycsw.services import csw


@pytest.mark.unit
def test_get_csw202_service_default_creation_map():
    service_id = "CSW_v2.0.2"
    service_config = {
        "fake_key1": "fake_value1",
    }
    mock_csw202_service_class = mock.MagicMock(spec=csw.Csw202Service)
    with mock.patch("pycsw.services.factory.utilities.lazy_import_dependency",
                    autospec=True) as mock_lazy_import:
        mock_lazy_import.return_value = mock_csw202_service_class
        service = factory.get_service(identifier=service_id,
                                      config=service_config)
        mock_lazy_import.assert_called_with("pycsw.services.csw",
                                            type_="Csw202Service")
        mock_csw202_service_class.from_config.assert_called_with(
            **service_config)


@pytest.mark.unit
def test_get_invalid_service():
    service_id = "fake_service"
    with pytest.raises(ValueError):
        service = factory.get_service(identifier=service_id, config={})
