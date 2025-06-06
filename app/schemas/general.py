from pydantic import BaseModel, Field

class ResponseModel(BaseModel):
    status: bool = Field(default=True)
    text: str
    kb: None | object = None