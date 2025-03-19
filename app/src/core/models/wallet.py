from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Numeric, UniqueConstraint
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .currency import Currency


class Wallet(Base):

    name: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="wallets")
    currencies: Mapped[list["Currency"]] = relationship(
        "Currency", back_populates="wallet", cascade="all, delete-orphan"
    )
    __table_args__ = (UniqueConstraint("user_id", "name", name="_user_wallet_name_uc"),)
