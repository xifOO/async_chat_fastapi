from pydantic import BaseModel, ConfigDict


class ResponseMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)
