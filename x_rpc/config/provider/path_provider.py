from typing import Dict

from x_rpc.config.provider import BaseConfigProvider, ConfigProviderType
from x_rpc.config.utils import parse_config_from_object
from x_rpc.plugin import PluginType, register_plugin
from x_rpc.utils.module import load_module_from_file_location


@register_plugin(PluginType.CONFIG_PROVIDER, ConfigProviderType.PATH)
class PathConfigProvider(BaseConfigProvider):
    def __init__(self, *args, **kwargs):
        self.options = None
        self.location = None
        self.encoding = None

    def set_options(self, options: Dict) -> None:
        self.options = options
        self.location = self.options.get("location", None)
        self.encoding = self.options.get("encoding", "utf8")

    def load(self, *args, **kwargs):
        """从文件路径加载配置 ."""
        if self.location is None:
            return {}
        config = load_module_from_file_location(self.location, self.encoding, *args, **kwargs)
        config = parse_config_from_object(config)
        return config
