from uuid import uuid4
from sqlalchemy import Column, String, Integer, Enum as SQLAlchemyEnum, TIMESTAMP, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pytz import timezone
from enum import Enum

# Enum for 2FA status
class TwoFAStatus(str, Enum):
    UNUSED = "unused"
    USED = "used"
    EXPIRED = "expired"

# Utility function to get the current time in IST
def get_ist_time():
    ist = timezone('Asia/Kolkata')
    return datetime.now(ist).replace(tzinfo=None)

class User(Base):
    __tablename__ = "credentials"

    employee_id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed password
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_sign_in = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    session_id = Column(String(36), nullable=False, unique=True, default=lambda: str(uuid4()))

    # Relationships
    attendance_records = relationship("AttendanceData", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordRestToken", back_populates="user", cascade="all, delete-orphan")

class AttendanceData(Base):
    __tablename__ = "attendancedata"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(255), ForeignKey("credentials.employee_id"), nullable=False)
    task_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    place_of_visit = Column(String(255))
    purpose_of_visit = Column(String(255))
    visiting_person_name = Column(String(255))
    employee_location = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="attendance_records")

class TwoFACode(Base):
    __tablename__ = "twofa_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    code = Column(String(6), nullable=False)  # 6-digit 2FA code
    created_at = Column(DateTime, default=get_ist_time)
    expires_at = Column(DateTime, nullable=False)
    used = Column(SQLAlchemyEnum(TwoFAStatus), default=TwoFAStatus.UNUSED)

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    employee_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class DynavacEmail(Base):
    __tablename__ = "dynavacemail"

    email = Column(String(255), nullable=False, unique=True, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    employee_id = Column(String(30), nullable=False, unique=True)

class PasswordRestToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(String(255), ForeignKey("credentials.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)

    user = relationship("User", back_populates="password_reset_tokens")
