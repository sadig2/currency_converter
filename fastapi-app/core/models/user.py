from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    username: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
