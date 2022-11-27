from datetime import datetime
from typing import List, Optional

from httpcore import URL
from httpx import Client, Cookies
from pydantic import Field
from requests.utils import cookiejar_from_dict
from typing_extensions import Self

from errors import (
    CookieExpired,
    LoginFiled,
    TorrentDuplicateError,
    UploadTorrentException,
)
from models.bangumi import BangumiResponse, My, Tag, UploadResponse
from utils import jsonlib as json
from utils.const import BANGUMI_MOE_HOST, PROJECT_ROOT
from utils.helpers import str2md5
from utils.net import Net
from utils.typedefs import StrOrPath

__all__ = ["Bangumi"]


class Bangumi(Net):
    base_url: URL = BANGUMI_MOE_HOST

    id: str = Field(alias="_id")
    username: str
    email_hash: str = Field(alias="emailHash")
    active: bool
    register_data: datetime = Field("regDate")
    team_ids: Optional[List[str]]
    group: str
    cookies: Cookies

    @classmethod
    def login_with_password(cls, username: str, password: str) -> Self:
        """使用用户名和密码来登录"""
        client = Client(
            base_url=BANGUMI_MOE_HOST,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
                "cache-control": "no-cache",
                "DNT": "1",
                "host": BANGUMI_MOE_HOST.host,
                "origin": "https://bangumi.moe",
                "referer": "https://bangumi.moe/",
            },
        )
        response = client.post(
            "/api/user/signin",
            json={"username": username, "password": str2md5(password)},
        )
        response.raise_for_status()
        json_data = json.loads(response.text)
        if not json_data["success"]:
            raise LoginFiled("登录失败，请检查您输入的用户名或密码是否正确。")
        result = cls.parse_obj(
            json_data["user"] | {"cookies": response.cookies}
        )
        result._client = client
        return result

    @classmethod
    def login_with_cookies(cls, path: StrOrPath) -> Self:
        """使用保存的cookies来登录"""
        with open(
            PROJECT_ROOT.joinpath(path).resolve(), encoding="utf-8"
        ) as file:
            json_data = json.load(file)
        cookiejar = cookiejar_from_dict(json_data)
        cookies = Cookies(cookiejar)
        # api/user/session
        client = Client(
            base_url=BANGUMI_MOE_HOST,
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
                "cache-control": "no-cache",
                "DNT": "1",
                "host": BANGUMI_MOE_HOST.host,
                "origin": "https://bangumi.moe",
                "referer": "https://bangumi.moe/",
            },
        )
        response = client.get("/api/user/session", cookies=cookies)
        response.raise_for_status()
        json_data = json.loads(response.text)
        if not json_data:
            raise CookieExpired("cookie 无效或已经过期，请尝试使用其它登录方式进行登录。")
        result = cls.parse_obj(json_data | {"cookies": cookies})
        client.cookies = cookies
        result._client = client
        return result

    def my(self) -> My:
        response = self.get("/api/torrent/my")
        response.raise_for_status()
        return My.parse_raw(response.text)

    def my_teams(self) -> List:
        """获取我的team"""
        # noinspection SpellCheckingInspection
        response = self.get("/api/team/myteam")
        response.raise_for_status()
        json_data = json.loads(response.text)
        return json_data or []

    def upload_torrent(self, path: StrOrPath) -> UploadResponse:
        """上传指定路径的种子文件"""
        path = PROJECT_ROOT.joinpath(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"种子文件不存在：{path}")
        response = self.post(
            "/api/v2/torrent/upload", files={"file": path.open("rb")}
        )
        response.raise_for_status()
        response_obj = BangumiResponse.parse_raw(response.text)
        if not response_obj.success:  # 若上传错误
            if "torrent same as" in response_obj.message:
                raise TorrentDuplicateError("种子文件重复，无法上传。")
            raise UploadTorrentException(response_obj.message or "上传遇到未知错误")
        return UploadResponse.parse_raw(response.text)

    def get_tag_misc(self) -> List[Tag]:
        response = self.get("/api/tag/misc")
        json_data = json.loads(response.text)
        return [Tag.parse_obj(i) for i in json_data]