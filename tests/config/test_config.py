from contextlib import contextmanager
from os import environ
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

import pytest

from x_rpc.config import Config
from x_rpc.exceptions import PyFileException


@contextmanager
def temp_path():
    """a simple cross platform replacement for NamedTemporaryFile"""
    with TemporaryDirectory() as td:
        yield Path(td, "file")


class ConfigTest:
    not_for_config = "should not be used"
    CONFIG_VALUE = "should be used"

    @property
    def ANOTHER_VALUE(self):
        return self.CONFIG_VALUE

    @property
    def another_not_for_config(self):
        return self.not_for_config


def test_load_from_object():
    config = Config()
    config.load_from_object(ConfigTest)
    assert "CONFIG_VALUE" in config
    assert config.CONFIG_VALUE == "should be used"
    assert "not_for_config" not in config


def test_load_from_instance():
    config = Config()
    config.load_from_object(ConfigTest())
    assert "CONFIG_VALUE" in config
    assert config.CONFIG_VALUE == "should be used"
    assert config.ANOTHER_VALUE == "should be used"
    assert "not_for_config" not in config
    assert "another_not_for_config" not in config


def test_load_from_object_string_exception():
    with pytest.raises(ImportError):
        config = Config()
        config.load_from_path("test_config.Config.test")


def test_auto_env_prefix():
    environ["XRPC_TEST_ANSWER"] = "42"
    assert Config().TEST_ANSWER == 42
    del environ["XRPC_TEST_ANSWER"]


def test_auto_bool_env_prefix():
    environ["XRPC_TEST_ANSWER"] = "True"
    assert Config().TEST_ANSWER is True
    del environ["XRPC_TEST_ANSWER"]


@pytest.mark.parametrize("env_prefix", [None, ""])
def test_empty_load_env_prefix(env_prefix):
    environ["XRPC_TEST_ANSWER"] = "42"
    config = Config(env_prefix=env_prefix)
    assert getattr(config, "TEST_ANSWER", None) == 42
    del environ["XRPC_TEST_ANSWER"]


def test_load_env_prefix_float_values():
    environ["MYAPP_TEST_ROI"] = "2.3"
    config = Config(env_prefix="MYAPP_")
    assert config.TEST_ROI == 2.3
    del environ["MYAPP_TEST_ROI"]


def test_env_prefix():
    environ["MYAPP_TEST_ANSWER"] = "42"
    config = Config(env_prefix="MYAPP_")
    assert config.TEST_ANSWER == 42
    del environ["MYAPP_TEST_ANSWER"]


def test_env_prefix_float_values():
    environ["MYAPP_TEST_ROI"] = "2.3"
    config = Config(env_prefix="MYAPP_")
    assert config.TEST_ROI == 2.3
    del environ["MYAPP_TEST_ROI"]


def test_env_prefix_string_value():
    environ["MYAPP_TEST_TOKEN"] = "somerandomtesttoken"
    config = Config(env_prefix="MYAPP_")
    assert config.TEST_TOKEN == "somerandomtesttoken"
    del environ["MYAPP_TEST_TOKEN"]


def test_load_from_file():
    other_config = dedent(
        """
    VALUE = 'some value'
    condition = 1 == 1
    if condition:
        CONDITIONAL = 'should be set'
    """
    )
    with temp_path() as config_path:
        config_path.write_text(other_config)
        config = Config()
        config.load_from_path(str(config_path))
        assert "VALUE" in config
        assert config.VALUE == "some value"
        assert "CONDITIONAL" in config
        assert config.CONDITIONAL == "should be set"
        assert "condition" not in config


def test_load_from_missing_file():
    with pytest.raises(IOError):
        config = Config()
        config.load_from_path("non-existent file")


def test_load_from_envvar():
    other_config = "VALUE = 'some value'"
    with temp_path() as config_path:
        config_path.write_text(other_config)
        environ["APP_CONFIG"] = str(config_path)
        config = Config()
        config.load_from_path("${APP_CONFIG}")
        assert "VALUE" in config
        assert config.VALUE == "some value"


def test_load_from_missing_envvar():
    with pytest.raises(IOError) as e:
        config = Config()
        config.load_from_path("non-existent variable")
        assert str(e.value) == (
            "The environment variable 'non-existent "
            "variable' is not set and thus configuration "
            "could not be loaded."
        )


def test_load_config_from_file_invalid_syntax():
    config = "VALUE = some value"
    with temp_path() as config_path:
        config_path.write_text(config)

        with pytest.raises(PyFileException):
            config = Config()
            config.load_from_path(config_path)


def test_overwrite_exisiting_config():
    config = Config()
    config.DEFAULT = 1

    class OtherConfig:
        DEFAULT = 2

    config.load_from_object(OtherConfig)
    assert config.DEFAULT == 2


def test_overwrite_exisiting_config_ignore_lowercase():
    config = Config()
    config.default = 1

    class OtherConfig:
        default = 2

    config.load_from_path(OtherConfig)
    assert config.default == 1


def test_missing_config():
    with pytest.raises(AttributeError, match="Config has no 'NON_EXISTENT'"):
        config = Config()
        _ = config.NON_EXISTENT


_test_setting_as_dict = {"TEST_SETTING_VALUE": 1}
_test_setting_as_class = type("C", (), {"TEST_SETTING_VALUE": 1})
_test_setting_as_module = str(
    Path(__file__).parent.parent / "static/app_test_config.py"
)


@pytest.mark.parametrize(
    "conf_object",
    [
        _test_setting_as_dict,
        _test_setting_as_class,
    ],
    ids=["from_dict", "from_class"],
)
def test_update_from_object(conf_object):
    config = Config()
    config.load_from_object(conf_object)
    assert config["TEST_SETTING_VALUE"] == 1


def test_update_from_path():
    config = Config()
    config.load_from_path(_test_setting_as_module)
    assert config["TEST_SETTING_VALUE"] == 1


def test_update_from_lowercase_key():
    d = {"test_setting_value": 1}
    config = Config()
    config.load_from_object(d)
    assert "test_setting_value" not in config


def test_setter():
    class SetterConfig(Config):
        @property
        def a(self) -> str:
            return self.b

        @a.setter
        def a(self, value):
            self.b = value + 1

    config = SetterConfig()
    config.a = 1
    assert config.b == 2
