import pytest

from x_rpc.utils.format import str_to_bool


def test_str_to_bool():
    assert str_to_bool("1") is True
    with pytest.raises(ValueError):
        assert str_to_bool("2") is False
