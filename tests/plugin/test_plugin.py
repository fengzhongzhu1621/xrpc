# -*- coding: utf-8 -*-

from x_rpc.plugin import PluginType, get_plugin_instance, register_plugin


@register_plugin(PluginType.UNITTEST, "unittest")
class Plugin:
    a = 1

    def __init__(self):
        self.b = 2


def test_register_plugin():
    plugin_instance = get_plugin_instance(PluginType.UNITTEST, "unittest")
    assert plugin_instance.a == 1
    assert plugin_instance.b == 2
