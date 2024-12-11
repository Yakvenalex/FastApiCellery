from pydantic import BaseModel, Field, ConfigDict
from fastapi import UploadFile


class FileUploadModel(BaseModel):
    lifetime_minutes: int = Field(..., ge=1, le=1440, description="Срок жизни от 1 до 1440 мин")
    file: UploadFile

    model_config = ConfigDict(arbitrary_types_allowed=True)