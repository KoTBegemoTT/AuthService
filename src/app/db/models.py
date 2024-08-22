from sqlalchemy import MetaData, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.types import ARRAY, BigInteger, Boolean, Numeric

from app.config import settings

schema = settings.db_schema

Base = declarative_base(
    metadata=MetaData(schema=schema),
)


class BaseTable(Base):  # type: ignore
    """Базовая модель."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class User(BaseTable):
    """Модель пользователя."""

    __tablename__ = 'lebedev_user'

    name: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[bytes]
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_vector: Mapped[list[float] | None] = mapped_column(
        ARRAY(Numeric(8, 7)),
    )
