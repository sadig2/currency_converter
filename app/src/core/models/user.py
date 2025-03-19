from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .wallet import Wallet


class User(Base):
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    wallets: Mapped[list["Wallet"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
