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
    torrents: List


class TagLocale(BaseModel):
    zh_cn: Optional[str]
    zh_tw: Optional[str]
    en: Optional[str]
    ja: Optional[str]


class Tag(BaseModel):
    id: str = Field(alias="_id")
    activity: bool
    locale: TagLocale
    name: str
    syn_lowercase: List[str]
    synonyms: List[str]
    type: str


class Uploader(BaseModel):
    id: str = Field(alias='_id')
    username: str
    email_hash: str = Field(alias="emailHash")


class Torrent(BaseModel):
    id: str = Field(alias="_id")
    title: str
    introduction: str
    comments: int
    downloads: int
    finished: int
    # noinspection SpellCheckingInspection
    leechers: int
    seeders: int
    publish_time: datetime
    magnet: str
    info_hash: str = Field(alias="infoHash")
    file_id: str
    team_id: Optional[str]
    # noinspection SpellCheckingInspection
    teamsync: Optional[Any]  # todo
    content: List[List[str]]
    title_index: Optional[List[str]] = Field(alias='titleIndex')
    size: str
    # noinspection SpellCheckingInspection
    btskey: str
    predicted_title: Optional[str]

    uploader_id: str
    uploader: Optional[Uploader]

    tag_ids: List[str]
    tags: Optional[List[Tag]]

    category_tag_id: str
    category_tag_: Optional[Tag]


class My(BaseModel):
    torrents: List[Torrent]
    page_count: int
