from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import Self

from utils import jsonlib as json

__all__ = ["BaseConfig", "BaseModel"]


class BaseConfig(object):
    json_dumps = json.dumps
    json_loads = json.loads


class BaseModel(PydanticBaseModel):
    def __new__(cls, *args, **kwargs) -> Self:
        cls.update_forward_refs()
        return super(BaseModel, cls).__new__(cls)

    class Config(BaseConfig, PydanticBaseModel.Config):
        pass
