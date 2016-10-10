"""Unit tests for pycsw.parameters."""

import pytest

from pycsw import parameters

pytestmark = pytest.mark.unit


class TestIntParameter:

    @pytest.mark.parametrize("allowed, value", [
        ([1], 1),
        (range(10, 11)),
    ])
    def test_validate(self, allowed, value):
        public_name = "my_param"
        int_param = parameters.IntParameter(public_name,
                                            allowed_values=allowed)
        int_param.validate(value)
