from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Numeric


class Base(DeclarativeBase):
    """Базовая модель."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'users'

    name: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[bytes]
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_vector: Mapped[list[float] | None] = mapped_column(ARRAY(Numeric(8, 7)))  # noqa: E501
