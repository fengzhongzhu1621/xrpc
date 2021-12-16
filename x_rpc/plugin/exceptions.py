from x_rpc.exceptions import XRPCException


class PluginException(XRPCException):
    pass


class PluginTypeNotFound(PluginException):
    pass
