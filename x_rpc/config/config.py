from inspect import getmembers, isclass, isdatadescriptor
from os import environ
from pathlib import Path
from typing import Any, Dict, Optional, Union

from x_rpc.utils.format import str_to_bool
from x_rpc.utils.module import load_module_from_file_location

XRPC_PREFIX = "XRPC_"


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
            self.load_environment_vars(env_prefix)
        else:
            self.load_environment_vars(XRPC_PREFIX)

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

    def load_environment_vars(self, prefix=XRPC_PREFIX):
        """
        Looks for prefixed environment variables and applies them to the
        configuration if present. This is called automatically when Sanic
        starts up to load environment variables into config.

        It will automatically hydrate the following types:

        - ``int``
        - ``float``
        - ``bool``

        Anything else will be imported as a ``str``.
        """
        for key, value in environ.items():
            if not key.startswith(prefix):
                continue

            _, config_key = key.split(prefix, 1)

            # 注意类型转换顺序
            for converter in (int, float, str_to_bool, str):
                try:
                    self[config_key] = converter(value)
                    break
                except ValueError:
                    pass

    def update_config(self, config: Union[bytes, str, dict, Any]):
        """从其它配置源中获取配置 ."""
        if isinstance(config, (bytes, str, Path)):
            config = load_module_from_file_location(location=config)

        if not isinstance(config, dict):
            cfg = {}
            if not isclass(config):
                # 获得对象/模块的所有属性
                cfg.update(
                    {
                        key: getattr(config, key)
                        for key in config.__class__.__dict__.keys()
                    }
                )

            # 获得类中的所有属性
            config = dict(config.__dict__)
            config.update(cfg)

        # 只保留大写的属性
        config = dict(filter(lambda i: i[0].isupper(), config.items()))

        self.update(config)

    load = update_config
