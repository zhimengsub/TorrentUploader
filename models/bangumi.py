from typing import List

from pydantic import Extra, Field

from models import BaseModel

__all__ = ["BangumiResponse", "UploadResponse", "Tag"]


class BangumiResponse(BaseModel):
    success: bool
    message: str = ""

    class Config(BaseModel.Config):
        extra = Extra.allow


class UploadResponse(BangumiResponse):
    file_id: str
    content: List[List[str]]
    torrents: List


class Tag(BaseModel):
    class TagLocale(BaseModel):
        zh_cn: str
        zh_tw: str
        en: str

    id: str = Field(alias="_id")
    activity: bool
    locale: TagLocale
    name: str
    syn_lowercase: List[str]
    synonyms: List[str]
    type: str
