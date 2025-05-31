from datetime import datetime
from pydantic import BaseModel, Field

class TimestampMixin(BaseModel):
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class OwnerMixin(BaseModel):
    ownerId: str = Field(..., alias="ownerId")