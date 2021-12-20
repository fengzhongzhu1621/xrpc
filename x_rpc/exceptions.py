class XRPCException(Exception):
    pass


class PyFileError(XRPCException):
    def __init__(self, file):
        super().__init__("could not execute config file %s", file)


class LoadFileException(XRPCException):
    """文件加载异常 ."""
    pass
