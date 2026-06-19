from typing import Iterable


class ApplicationException(Exception):
    """Application错误"""


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


class PredictionNotFoundInResponse(ApplicationException):
    """没有在上传种子的响应中找到预测标题"""

    def __init__(self):
        super().__init__("没有在上传种子的响应中找到预测标题")


class BestPredictionNotFound(ApplicationException):
    """未找到最匹配的预测标题"""

    def __init__(self):
        super().__init__("未找到最匹配的预测标题")


class PublishFailed(ApplicationException):
    """发布失败"""


class GuiException(Exception):
    """GUI 错误"""


class DirectoryWatchFailed(GuiException):
    """目录监控失败"""

    def __init__(self, failedDirs: Iterable[str]):
        self.failedDirs = failedDirs


class SqlError(GuiException):
    def __init__(self, err: str):
        super().__init__(err)
