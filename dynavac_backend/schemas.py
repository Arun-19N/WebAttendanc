from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class TwoFAStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"


class TwoFACodeBase(BaseModel):
    email: EmailStr
    code: str
    created_at: datetime
    expires_at: datetime
    used: TwoFAStatus

    class Config:
        from_attributes = True


class TwoFACodeCreate(BaseModel):
    email: EmailStr
    code: str
    expires_at: datetime


class DynavacEmailBase(BaseModel):
    email: EmailStr
    created_at: datetime
    employee_id: str


'''class DynavacEmailCheck(BaseModel):
    email: str


class DynavacEmployeeID(BaseModel):
    employee_id: str
'''


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetVerify(BaseModel):
    token: str
    new_password: str


class UserCreate(BaseModel):
    employee_id: str
    email: EmailStr
    password: str
    name: str
    designation: str


class UserResponse(BaseModel):
    employee_id: str
    email: EmailStr
    name: str
    designation: str
    session_id: str
    created_at: datetime
    last_sign_in: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AttendanceCreate(BaseModel):
    task_name: str
    place_of_visit: Optional[str] = None
    purpose_of_visit: Optional[str] = None
    visiting_person_name: Optional[str] = None
    employee_location: Optional[str] = None


class AttendanceResponse(BaseModel):
    task_id: int
    employee_id: str
    task_name: str
    designation: str
    place_of_visit: Optional[str] = None
    purpose_of_visit: Optional[str] = None
    visiting_person_name: Optional[str] = None
    employee_location: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class VerifyRegistrationRequest(BaseModel):
    email: EmailStr
    code: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str