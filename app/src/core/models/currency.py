from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Numeric, Date, func
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from .wallet import Wallet


class Currency(Base):

    label: Mapped[str] = mapped_column(String(3))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0.00, nullable=False
    )
    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="currencies")
