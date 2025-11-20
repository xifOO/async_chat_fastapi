from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TimeStampMixin(BaseModel):
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: Optional[datetime] = None
