from pydantic import BaseModel, ConfigDict


class BaseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
