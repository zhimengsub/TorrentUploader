from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel as PydanticBaseModel, Field

from utils import jsonlib as json

__all__ = ["BaseModel", "BangumiUser"]


class BaseModel(PydanticBaseModel):
    class Config(PydanticBaseModel.Config):
        json_loads = json.loads
        json_dumps = json.dumps


class BangumiUser(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email_hash: str = Field(alias="emailHash")
    active: bool
    register_data: datetime = Field("regDate")
    team_ids: Optional[List[str]]
    group: str
    cookies: str
