class ApplicationException(Exception):
    ...


class LoginFiled(ApplicationException):
    """登录错误"""


class CookieExpired(ApplicationException):
    """cookie 过期"""


class UploadTorrentException(ApplicationException):
    """上传种子错误"""


class TorrentDuplicateError(UploadTorrentException):
    """种子重复"""
