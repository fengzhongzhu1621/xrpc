from enum import IntEnum, unique
from typing import Any, Dict, Optional, Union

from x_rpc.standard import status
from x_rpc.standard.http import STATUS_CODES


@unique
class ErrorType(IntEnum):
    FRAMEWORK = 1  # 框架错误
    BUSINESS = 2  # 业务错误


@unique
class ErrorCode(IntEnum):
    SUCCESS = 0  # 成功
    ERR_UNKNOWN = 999  # 未知异常


class XRPCException(Exception):
    """异常基类 ."""
    pass


class XRPCBaseException(XRPCException):
    def __init__(self, exception_type: Union[int, ErrorType], code: Union[int, ErrorCode], message: str):
        # 异常类型
        self.exception_type = exception_type.value if isinstance(exception_type, ErrorType) else exception_type
        # 错误码
        self.code = code.value if isinstance(code, ErrorCode) else code
        self.message = message  # 错误原因


class PyFileException(XRPCException):
    def __init__(self, file):
        super().__init__("could not execute config file %s", file)


class UnknownException(XRPCBaseException):
    def __init__(self, message):
        super().__init__(ErrorType.FRAMEWORK, ErrorCode.ERR_UNKNOWN, message)


class FrameException(XRPCBaseException):
    """框架异常基类 ."""

    def __init__(self, code, message):
        super().__init__(ErrorType.FRAMEWORK, code, message)


class BusinessException(XRPCBaseException):
    """业务异常基类 ."""

    def __init__(self, code, message):
        super().__init__(ErrorType.BUSINESS, code, message)


class HttpException(XRPCBaseException):
    message: str = ""

    def __init__(self,
                 message: Optional[Union[str, bytes]] = None,
                 status_code: Optional[int] = None,
                 context: Optional[Dict[str, Any]] = None,
                 extra: Optional[Dict[str, Any]] = None):

        self.context = context
        self.extra = extra
        if message is None:
            if self.message:
                # 自定义错误信息
                message = self.message
            elif status_code is not None:
                # HTTP错误标准信息
                msg: bytes = STATUS_CODES.get(status_code, b"")
                message = msg.decode("utf8")
        # HTTP状态码
        if status_code is not None:
            self.status_code = status_code
        super().__init__(ErrorType.FRAMEWORK, self.status_code, message)


class NotFound(HttpException):
    """
    **Status**: 404 Not Found
    """

    status_code = status.HTTP_404_NOT_FOUND


class InvalidUsage(HttpException):
    """
    **Status**: 400 Bad Request
    """

    status_code = status.HTTP_400_BAD_REQUEST


class MethodNotSupported(HttpException):
    """
    **Status**: 405 Method Not Allowed
    """

    status_code = status.HTTP_405_METHOD_NOT_ALLOWED

    def __init__(self, message, method, allowed_methods):
        super().__init__(message)
        self.method = method
        self.headers = {"Allow": ", ".join(allowed_methods)}


class ServerError(HttpException):
    """
    **Status**: 500 Internal Server Error
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailable(HttpException):
    """
    **Status**: 503 Service Unavailable

    The server is currently unavailable (because it is overloaded or
    down for maintenance). Generally, this is a temporary state.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class URLBuildError(ServerError):
    """
    **Status**: 500 Internal Server Error
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class FileNotFound(NotFound):
    """
    **Status**: 404 Not Found
    """

    def __init__(self, message, path, relative_url):
        super().__init__(message)
        self.path = path
        self.relative_url = relative_url


class RequestTimeout(HttpException):
    """The Web server (running the Web site) thinks that there has been too
    long an interval of time between 1) the establishment of an IP
    connection (socket) between the client and the server and
    2) the receipt of any data on that socket, so the server has dropped
    the connection. The socket connection has actually been lost - the Web
    server has 'timed out' on that particular socket connection.
    """

    status_code = status.HTTP_408_REQUEST_TIMEOUT


class PayloadTooLarge(HttpException):
    """
    **Status**: 413 Payload Too Large
    """

    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


class HeaderNotFound(InvalidUsage):
    """
    **Status**: 400 Bad Request
    """


class InvalidHeader(InvalidUsage):
    """
    **Status**: 400 Bad Request
    """


class ContentRangeError(HttpException):
    """
    **Status**: 416 Range Not Satisfiable
    """

    status_code = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE

    def __init__(self, message, content_range):
        super().__init__(message)
        self.headers = {"Content-Range": f"bytes */{content_range.total}"}


class HeaderExpectationFailed(HttpException):
    """
    **Status**: 417 Expectation Failed
    """

    status_code = status.HTTP_417_EXPECTATION_FAILED


class Forbidden(HttpException):
    """
    **Status**: 403 Forbidden
    """

    status_code = status.HTTP_403_FORBIDDEN


class InvalidRangeType(ContentRangeError):
    """
    **Status**: 416 Range Not Satisfiable
    """

    status_code = status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE


class Unauthorized(HttpException):
    """
    **Status**: 401 Unauthorized

    :param message: Message describing the exception.
    :param status_code: HTTP Status code.
    :param scheme: Name of the authentication scheme to be used.

    When present, kwargs is used to complete the WWW-Authentication header.

    Examples::

        # With a Basic auth-scheme, realm MUST be present:
        raise Unauthorized("Auth required.",
                           scheme="Basic",
                           realm="Restricted Area")

        # With a Digest auth-scheme, things are a bit more complicated:
        raise Unauthorized("Auth required.",
                           scheme="Digest",
                           realm="Restricted Area",
                           qop="auth, auth-int",
                           algorithm="MD5",
                           nonce="abcdef",
                           opaque="zyxwvu")

        # With a Bearer auth-scheme, realm is optional so you can write:
        raise Unauthorized("Auth required.", scheme="Bearer")

        # or, if you want to specify the realm:
        raise Unauthorized("Auth required.",
                           scheme="Bearer",
                           realm="Restricted Area")
    """

    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message, status_code=None, scheme=None, **kwargs):
        super().__init__(message, status_code)

        # if auth-scheme is specified, set "WWW-Authenticate" header
        if scheme is not None:
            values = ['{!s}="{!s}"'.format(k, v) for k, v in kwargs.items()]
            challenge = ", ".join(values)

            self.headers = {
                "WWW-Authenticate": f"{scheme} {challenge}".rstrip()
            }


class LoadFileException(HttpException):
    pass


class InvalidSignal(HttpException):
    pass


class WebsocketClosed(HttpException):
    message = "Client has closed the websocket connection"
