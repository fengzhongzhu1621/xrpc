from inspect import getmembers, isdatadescriptor
from pathlib import Path
from typing import Any, Dict, Optional, Union

from x_rpc.config.constants import XRPC_PREFIX
from x_rpc.config.provider import ConfigProviderType
from x_rpc.config.utils import parse_config_from_object
from x_rpc.plugin import PluginType, get_plugin_instance


class DescriptorMeta(type):
    def __init__(cls, *_):
        # 获得类中所有的可修改属性名
        cls.__setters__ = {name for name, _ in getmembers(cls, cls._is_setter)}

    @staticmethod
    def _is_setter(member: object):
        """判断一个类方法是否是属性设置方法 ."""
        # isdatadescriptor: 如果对象是数据描述符，则返回True，数字标识符有__get__ 和__set__属性； 通常也有__name__和__doc__属性
        return isdatadescriptor(member) and hasattr(member, "setter")


class Config(dict, metaclass=DescriptorMeta):
    """配置字典 ."""

    def __init__(
        self,
        defaults: Dict[str, Union[str, bool, int, float, None]] = None,
        env_prefix: Optional[str] = XRPC_PREFIX
    ):
        defaults = defaults or {}
        super().__init__(defaults)

        # 根据前缀从环境变量加载配置
        if env_prefix and env_prefix != XRPC_PREFIX:
            options = {
                "prefix": env_prefix,
            }
        else:
            options = {
                "prefix": XRPC_PREFIX,
            }
        self.load_environment_vars(options)

    def __getattr__(self, attr):
        """使用点号获取实例属性，如果属性不存在就自动调用__getattr__方法 ."""
        try:
            return self[attr]
        except KeyError as ke:
            raise AttributeError(f"Config has no '{ke.args[0]}'")

    def __setattr__(self, attr, value) -> None:
        """设置字典的值 ."""
        if attr in self.__class__.__setters__:
            try:
                # 自定义属性值设置
                super().__setattr__(attr, value)
            except AttributeError:
                ...
            else:
                return None
        self.update({attr: value})

    def __setitem__(self, attr, value) -> None:
        """给key赋值 ."""
        self.update({attr: value})

    def load_environment_vars(self, options: Dict) -> None:
        """从环境变量加载配置 ."""
        provider = get_plugin_instance(PluginType.CONFIG_PROVIDER, ConfigProviderType.ENV)
        provider.set_options(options)
        env_config = provider.load()
        self.update(env_config)

    def load_from_object(self, obj):
        if not isinstance(obj, (bytes, str, Path)):
            config = parse_config_from_object(obj)
            self.update(config)

    def load_from_path(self, path: Union[bytes, str, dict, Any]) -> None:
        """从指定路径获取配置 ."""
        if isinstance(path, (bytes, str, Path)):
            provider = get_plugin_instance(PluginType.CONFIG_PROVIDER, ConfigProviderType.PATH)
            options = {
                "location": path,
                "encoding": "utf8",
            }
            provider.set_options(options)
            config = provider.load()
            self.update(config)
