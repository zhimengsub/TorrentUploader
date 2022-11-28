from datetime import datetime
from typing import Any, List, Optional

from pydantic import Extra, Field

from models import BaseModel


# __all__ = ["BangumiResponse", "UploadResponse", "Tag"]


class BangumiResponse(BaseModel):
    success: bool
    message: str = ""

    class Config(BaseModel.Config):
        extra = Extra.allow


class UploadResponse(BangumiResponse):
    file_id: str
    content: List[List[str]]
    torrents: List["Torrent"]

    @property
    def predicted_titles(self) -> List[str]:
        """预测的标题"""
        result = []
        for torrent in self.torrents:
            if (
                hasattr(torrent, "predicted_title")
                and (title := torrent.predicted_title) is not None
            ):
                result.append(title)
        return result


class TagLocale(BaseModel):
    """tag 本地化"""

    zh_cn: Optional[str]
    """简中翻译"""
    zh_tw: Optional[str]
    """繁中翻译"""
    en: Optional[str]
    """英文翻译"""
    ja: Optional[str]
    """日语翻译"""


class Tag(BaseModel):
    id: str = Field(alias="_id")
    activity: bool
    locale: TagLocale
    """本地化"""
    name: str
    """名称"""
    syn_lowercase: List[str]
    synonyms: List[str]
    type: str
    """类型"""


class Uploader(BaseModel):
    """上传者"""

    id: str = Field(alias="_id")
    username: str
    """用户名"""
    email_hash: str = Field(alias="emailHash")
    """email 的 md5 值"""


class Torrent(BaseModel):
    id: str = Field(alias="_id")
    title: str
    """标题"""
    introduction: str
    """介绍"""
    comments: int
    """评论数"""
    downloads: int
    """下载数"""
    finished: int
    # noinspection SpellCheckingInspection
    leechers: int
    seeders: int
    publish_time: datetime
    """发布的时间"""
    magnet: str
    """磁力链接"""
    info_hash: str = Field(alias="infoHash")
    file_id: str
    team_id: Optional[str]
    # noinspection SpellCheckingInspection
    teamsync: Optional[Any]  # todo
    content: List[List[str]]
    title_index: Optional[List[str]] = Field(alias="titleIndex")
    size: str
    """大小"""
    # noinspection SpellCheckingInspection
    btskey: str
    predicted_title: Optional[str]
    """预测的标题"""

    uploader_id: str
    uploader: Optional[Uploader]

    tag_ids: List[str]
    tags: Optional[List[Tag]]

    category_tag_id: str
    category_tag_: Optional[Tag]


class My(BaseModel):
    torrents: List[Torrent]
    page_count: int
