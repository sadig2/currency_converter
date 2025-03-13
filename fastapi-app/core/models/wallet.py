from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Numeric
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Wallet(Base):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    currency: Mapped[str] = mapped_column(String(3))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="wallets")
