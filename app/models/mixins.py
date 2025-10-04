from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column


class IntegerIDMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )
