import pytest

from pycsw.services.csw import cswbase
from pycsw.services.csw import csw202

@pytest.mark.unit
class TestCswService:

    def test_identifier(self):
        service = cswbase.CswService()
        assert service.identifier == "CSW_v"


@pytest.mark.unit
class TestCsw202Service:

    def test_identifier(self):
        service = csw202.Csw202Service()
        assert service.identifier == "CSW_v2.0.2"
