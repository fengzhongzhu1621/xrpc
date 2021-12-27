from os import environ
from typing import Dict

from x_rpc.config.constants import XRPC_PREFIX
from x_rpc.config.provider import BaseConfigProvider, ConfigProviderType
from x_rpc.plugin import PluginType, register_plugin
from x_rpc.utils.format import str_to_bool


@register_plugin(PluginType.CONFIG_PROVIDER, ConfigProviderType.ENV)
class EnvConfigProvider(BaseConfigProvider):
    def __init__(self, *args, **kwargs):
        self.options = None
        self.prefix = XRPC_PREFIX

    def set_options(self, options: Dict) -> None:
        self.options = options
        self.prefix = self.options.get("prefix", XRPC_PREFIX)

    def load(self):
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
        config = {}
        for key, value in environ.items():
            # 过滤前缀
            if not key.startswith(self.prefix):
                continue
            # 获得配置key
            _, config_key = key.split(self.prefix, 1)
            # 将配置值转换为指定类型，注意类型转换顺序
            for converter in (int, float, str_to_bool, str):
                try:
                    config[config_key] = converter(value)
                    break
                except ValueError:
                    pass
        return config
