from typing import Iterable


class ApplicationException(Exception):
    ...


class LoginFailed(ApplicationException):
    """登录错误"""


class AccountTeamError(ApplicationException):
    """所属团队错误"""


class CookieExpired(ApplicationException):
    """cookie 过期"""


class UploadTorrentException(ApplicationException):
    """上传种子错误"""


class TorrentDuplicateError(UploadTorrentException):
    """种子重复"""


class PublishFailed(ApplicationException):
    """发布失败"""


class GuiException(Exception):
    ...


class DirectoryWatchFailed(GuiException):
    """目录监控失败"""

    def __init__(self, failedDirs: Iterable[str]):
        self.failedDirs = failedDirs


class SqlError(GuiException):
    def __init__(self, err: str):
        super().__init__(err)
