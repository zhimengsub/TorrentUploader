import hashlib


def str2md5(target: str) -> str:
    """将目标字符串用 md5 加密"""
    hl = hashlib.md5()
    hl.update(target.encode(encoding='utf-8'))
    return hl.hexdigest()
