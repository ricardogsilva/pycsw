"""Unit tests for pycsw.utilities."""

import pytest
import mock

from pycsw import utilities

pytestmark = pytest.mark.unit


class TestLazyContainer:

    @pytest.mark.parametrize("class_paths", [
        (["bogus.code1", "bogus.code2"]),
        ([("bogus.code3", {"my_arg1": "value1"})]),
    ])
    def test_iter(self, class_paths):
        container = utilities.LazyList(contents=class_paths)
        with mock.patch.object(container, "_instantiate_item",
                               autospec=True) as mocked_instantiate:
            list(container)
            mocked_instantiate.assert_has_calls(
                [mock.call(path) for path in class_paths]
            )

    def test_instantiate_item_with_class_path(self):
        fake_class_path = "bogus1.code"
        with mock.patch("pycsw.utilities.lazy_import_dependency",
                        autospec=True) as mock_lazy_import:
            container = utilities.LazyList(contents=[fake_class_path])
            container._instantiate_item(fake_class_path)
            mocked_generic_class = mock_lazy_import.return_value
            mock_lazy_import.assert_called_with(
                *(fake_class_path.rpartition(".")[::2]))
            mocked_generic_class.assert_called()

    def test_instantiate_item_with_object(self):
        some_object = None
        container = utilities.LazyList(contents=[some_object])
        response = container._instantiate_item(some_object)
        assert some_object == response


