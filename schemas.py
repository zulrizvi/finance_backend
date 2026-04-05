import datetime as dt
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from models import Role, Status, RecordType


## Auth

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.VIEWER


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


### Users

class UserResponse(BaseModel):
    id: int
    email: str
    role: Role
    status: Status
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateRoleRequest(BaseModel):
    role: Role


class UpdateStatusRequest(BaseModel):
    status: Status


## Financial Records

class RecordCreate(BaseModel):
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None


class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[dt.date] = None
    notes: Optional[str] = None


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


### Dashboard

class CategoryTotal(BaseModel):
    category: str
    total: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    category_totals: list[CategoryTotal]
    recent_records: list[RecordResponse]
