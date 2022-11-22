class LoginFiled(Exception):
    """登录错误"""


class UploadTorrentException(Exception):
    """上传种子错误"""


class TorrentDuplicateError(UploadTorrentException):
    """种子重复"""
