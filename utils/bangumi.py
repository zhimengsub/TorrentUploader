from pathlib import Path
from typing import Union

from httpx import Client

from errors import LoginFiled, TorrentDuplicateError
from models import BangumiUser
from utils.const import BANGUMI_MOE_HOST
from utils.helpers import str2md5

client = Client(base_url=BANGUMI_MOE_HOST)


def login_by_password(username: str, password: str) -> BangumiUser:
    """登录"""
    # https://bangumi.moe/api/user/signin
    response = client.post(
        "/api/user/signin",
        json={"username": username, "password": str2md5(password)},
    )
    response.raise_for_status()
    json_data = response.json()
    if not json_data["success"]:  # 若登录失败
        raise LoginFiled("登录失败，请检查您输入的用户名或密码是否正确。")
    return BangumiUser.parse_obj(
        json_data["user"] | {"cookies": response.headers["set-cookie"]}
    )


def upload_torrent(path: Union[str, Path]):
    """上传种子文件"""
    # https://bangumi.moe/api/v2/torrent/upload
    response = client.post(
        "/api/user/signin",
        files={"torrent": Path(path).open("rb")},
    )
    response.raise_for_status()
    json_data = response.json()
    if not json_data["success"]:  # 若上传错误
        if "torrent same as" in json_data["message"]:
            raise TorrentDuplicateError("种子文件重复，无法上传。")
