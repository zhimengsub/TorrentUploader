from pydantic import BaseModel as PydanticBaseModel

from utils import jsonlib as json

__all__ = ["BaseModel"]


class BaseModel(PydanticBaseModel):
    class Config(PydanticBaseModel.Config):
        json_loads = json.loads
        json_dumps = json.dumps
