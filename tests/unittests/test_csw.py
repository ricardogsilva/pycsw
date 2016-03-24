import pytest

from pycsw.services import csw

@pytest.mark.unit
class TestCswService:

    def test_identifier(self):
        service = csw.CswService()
        assert service.identifier == "CSW_v"

    def test_creation_from_config(self):
        service = csw.CswService.from_config()
        assert service.identifier == "CSW_v"


@pytest.mark.unit
class TestCsw202Service:

    def test_identifier(self):
        service = csw.Csw202Service()
        assert service.identifier == "CSW_v2.0.2"

    def test_creation_from_config(self):
        service = csw.Csw202Service.from_config()
        assert service.identifier == "CSW_v2.0.2"
