from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Numeric, Date, func
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ExchangeRate(Base):

    code: Mapped[str] = mapped_column(String(3))
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    date: Mapped[datetime] = mapped_column(server_default=func.now())
