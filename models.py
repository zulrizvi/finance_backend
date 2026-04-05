import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
from database import Base


class Role(str, enum.Enum):
    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    ADMIN = "ADMIN"


class Status(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class RecordType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)
    status = Column(Enum(Status), default=Status.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(RecordType), nullable=False)
    category = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
