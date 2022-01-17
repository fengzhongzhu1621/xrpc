import pytest

from x_rpc.exceptions import BusinessException, ErrorCode, ErrorType, FrameException, NotFound, UnknownException
from x_rpc.standard import status


class TestUnknownException:
    def test_raises(self):
        message = "error message"
        with pytest.raises(UnknownException) as exc_info:
            raise UnknownException(message)
        err_args = exc_info.value
        assert err_args.code == ErrorCode.ERR_UNKNOWN.value
        assert err_args.exception_type == ErrorType.FRAMEWORK.value
        assert err_args.message == message


class TestFrameException:
    def test_raises(self):
        message = "error message"
        with pytest.raises(FrameException) as exc_info:
            raise FrameException(ErrorCode.ERR_UNKNOWN, message)
        err_args = exc_info.value
        assert err_args.code == ErrorCode.ERR_UNKNOWN.value
        assert err_args.exception_type == ErrorType.FRAMEWORK.value
        assert err_args.message == message


class TestBusinessException:
    def test_raises(self):
        message = "error message"
        with pytest.raises(BusinessException) as exc_info:
            raise BusinessException(ErrorCode.ERR_UNKNOWN, message)
        err_args = exc_info.value
        assert err_args.code == ErrorCode.ERR_UNKNOWN.value
        assert err_args.exception_type == ErrorType.BUSINESS.value
        assert err_args.message == message


class TestNotFound:
    def test_raises(self):
        with pytest.raises(NotFound) as exc_info:
            raise NotFound()
        err_args = exc_info.value
        assert err_args.code == status.HTTP_404_NOT_FOUND
        assert err_args.code == err_args.status_code
        assert err_args.exception_type == ErrorType.FRAMEWORK.value
        assert err_args.context is None
        assert err_args.message is None
        assert err_args.extra is None
