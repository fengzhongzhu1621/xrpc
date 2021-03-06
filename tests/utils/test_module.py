import inspect
from pathlib import Path
from types import ModuleType

import pytest

from x_rpc.config import Config
from x_rpc.exceptions import LoadFileException
from x_rpc.utils.module import import_string, load_module_from_file_location


def test_import_string_class():
    obj = import_string("x_rpc.config.Config")
    assert isinstance(obj, Config)


def test_import_string_module():
    module = import_string("x_rpc.config.config")
    assert inspect.ismodule(module)


def test_import_string_exception():
    with pytest.raises(ImportError):
        import_string("test.test.test")


def test_load_module_from_file_location_with_param(monkeypatch):
    monkeypatch.setenv("STATIC", "static")
    model = load_module_from_file_location(
        str(Path(__file__).parent / "${STATIC}" / "app_test_config.py")
    )
    assert model.TEST_SETTING_VALUE == 1


@pytest.fixture
def loaded_module_from_file_location():
    return load_module_from_file_location(
        str(Path(__file__).parent / "static" / "app_test_config.py")
    )


@pytest.mark.dependency(name="test_load_module_from_file_location")
def test_load_module_from_file_location(loaded_module_from_file_location):
    assert isinstance(loaded_module_from_file_location, ModuleType)
    assert loaded_module_from_file_location.TEST_SETTING_VALUE == 1


@pytest.mark.dependency(depends=["test_load_module_from_file_location"])
def test_loaded_module_from_file_location_name(
    loaded_module_from_file_location,
):
    name = loaded_module_from_file_location.__name__
    if "C:\\" in name:
        name = name.split("\\")[-1]
    assert name == "app_test_config"


def test_load_module_from_file_location_with_non_existing_env_variable():
    with pytest.raises(
        LoadFileException,
        match="The following environment variables are not set: MuuMilk",
    ):
        load_module_from_file_location("${MuuMilk}")
