from uuid import uuid4
from typing import Optional
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from security import get_password_hash
from models import User
from datetime import datetime, timedelta
from pytz import timezone
import random
from models import TwoFACode
from schemas import TwoFAStatus
from config import EMAIL_PASSWORD, EMAIL_SENDER, SMTP_PORT, SMTP_SERVER
from fastapi import HTTPException, status
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, to_email):
    # Your Google Workspace email credentials
    from_email = EMAIL_SENDER  # Your custom email address
    password = EMAIL_PASSWORD  # Use your app password if 2FA is enabled
    '''print(f"EMAIL_SENDER: {from_email}")
    print(f"pass: {password}")
    print(f"SMTP_PORT: {SMTP_PORT}")
    print(f"SMTP_SERVER: {SMTP_SERVER}")'''

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Google Workspace SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(from_email, password)  # Log in to your Google Workspace account
            server.send_message(msg)  # Send the email
            print("Email sent successfully!")
            return True
    except smtplib.SMTPAuthenticationError:
        print("Invalid credentials. Please check your email address and password.")
        return False
    except smtplib.SMTPConnectError:
        print("Unable to connect to the SMTP server. Please check your connection settings.")
    except Exception as e:
        print(f"Failed to send email")
        return False

def get_ist_time():
    ist = timezone("Asia/Kolkata")
    return datetime.now(ist).replace(tzinfo=None)


def create_pending_user(db: Session, user: schemas.UserCreate):
    try:
        pending_user = models.PendingUser(
            email=user.email,
            employee_id=user.employee_id,
            name=user.name,
            designation=user.designation,
            password_hash=get_password_hash(user.password)
        )
        db.add(pending_user)
        db.commit()
        db.refresh(pending_user)
        return pending_user

    except IntegrityError as e:
        db.rollback()

        # Explicitly detect duplicate entry clearly
        error_message = str(e.orig)
        if "Duplicate entry" in error_message:
            if "employee_id" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employee ID '{user.employee_id}' already exists. Please use a unique employee ID."
                )
            elif "email" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{user.email}' already exists. Please use a unique email address."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate entry detected. Please ensure unique values for required fields."
                )

        # General database integrity errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error encountered."
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error"
        )

def get_pending_user_by_email(db: Session, email: str):
    try:
        return db.query(models.PendingUser).filter(models.PendingUser.email == email).first()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving pending user by email")
    except Exception as e:
        raise ValueError(f"Unexpected error")


def create_user_from_pending(db: Session, pending_user: models.PendingUser):
    try:
        user = models.User(
            employee_id=pending_user.employee_id,
            email=pending_user.email,
            password=pending_user.password_hash,
            name=pending_user.name,
            designation=pending_user.designation,
            session_id=str(uuid4())
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error creating user from pending user")
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while creating user from pending user")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error")


def delete_pending_user(db: Session, email: str):
    try:
        db.query(models.PendingUser).filter(models.PendingUser.email == email).delete()
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while deleting pending user")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error")


'''def create_user(db: Session, user: schemas.UserCreate):
    try:
        session_id = str(uuid4())  # Generate unique session ID
        db_user = User(
            email=user.email,
            password=user.password,
            name=user.name,
            designation=user.designation,
            session_id=session_id,  # Assign session_id to the new user
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error creating user: {e.orig}")
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while creating user: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error: {str(e)}")'''


def get_user_by_email(db: Session, email: str):
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving user by email")
    except Exception as e:
        raise ValueError(f"Unexpected error")


def get_user_by_employee_id(db: Session, employee_id: str):
    try:
        return db.query(User).filter(User.employee_id == employee_id).first()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving user by employee ID")
    except Exception as e:
        raise ValueError(f"Unexpected error")

def check_dynavac_mail(db: Session, email: str):
    try:
        result = db.query(models.DynavacEmail).filter(models.DynavacEmail.email == email).first()
        if result:
            return True
        else:
            return False
    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving user by email")
    except Exception as e:
        raise ValueError(f"Unexpected error")

def check_dynavac_employee_id(db: Session, employee_id: str):
    try:
        result = db.query(models.DynavacEmail).filter(models.DynavacEmail.employee_id == employee_id).first()

        if result:
            return True
        else:
            return False

    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving user by employee ID")
    except Exception as e:
        raise ValueError(f"Unexpected error")


def generate_and_send_2fa_code(email: str, db: Session):
    try:
        email = email.lower()
        code = str(random.randint(100000, 999999))
        expires_at = get_ist_time() + timedelta(minutes=5)
        two_fa_code = models.TwoFACode(
            email=email,
            code=code,
            created_at=get_ist_time(),
            expires_at=expires_at,
            used=models.TwoFAStatus.UNUSED
        )
        db.add(two_fa_code)
        db.commit()
        #print("Verification code for {email} is {code}")

        email_subject = "Your 2FA Verification Code"
        email_body = f'''Hello,

        This email contains your two-factor authentication (2FA) verification code for your Dynavac account. Please use the following code to complete your login:

        Verification Code: {code}

        This code will expire in 5 minutes. If you did not request this code, please contact us immediately.

        Thank you,

        Dynavac India Pvt. Ltd.'''

    # Explicitly handle sending errors clearly
        email_sent = send_email(
            subject=email_subject,
            body=email_body,
            to_email=email
        )

        if not email_sent:
            # Clearly handle failure (e.g., rollback creation, log error clearly in DB logs, alerts, etc.)
            db.delete(two_fa_code)  # Revert DB entry clearly as sending failed explicitly
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later."
            )

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while generating 2FA code: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error: {str(e)}")


def get_twofa_code_by_email_and_code(db: Session, email: str, code: str):
    try:
        return db.query(models.TwoFACode).filter(
            models.TwoFACode.email == email,
            models.TwoFACode.code == code
        ).first()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error while retrieving 2FA code: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")


def mark_twofa_code_as_expired(db: Session, email: str):
    try:
        twofa_code = db.query(models.TwoFACode).filter(
            models.TwoFACode.email == email,
            models.TwoFACode.used == models.TwoFAStatus.UNUSED
        ).first()
        if twofa_code:
            twofa_code.used = models.TwoFAStatus.EXPIRED
            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while marking 2FA code as expired: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error: {str(e)}")


def create_attendance(db: Session, attendance: schemas.AttendanceCreate, employee_id: str, designation: str):
    try:
        db_attendance = models.AttendanceData(
            employee_id=employee_id,
            designation=designation,
            task_name=attendance.task_name,
            place_of_visit=attendance.place_of_visit,
            purpose_of_visit=attendance.purpose_of_visit,
            visiting_person_name=attendance.visiting_person_name,
            employee_location=attendance.employee_location,
        )
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)
        return db_attendance
    except IntegrityError as e:
        db.rollback()
        if "a foreign key constraint fails" in str(e.orig):
            raise ValueError(
                f"Employee ID '{employee_id}' does not exist. Ensure the employee is registered before creating attendance.")
        else:
            raise ValueError(f"Error creating attendance record: {e.orig}")
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Database error while creating attendance record: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Unexpected error: {str(e)}")


def validate_session_id(db: Session, email: str, session_id: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user or user.session_id != session_id:
        return None
    return user


def update_session_id(db: Session, user: User) -> str:
    new_session_id = str(uuid4())
    user.session_id = new_session_id
    user.last_sign_in = get_ist_time()
    db.commit()
    db.refresh(user)
    return new_session_id

def cleanup_expired_twofa_codes(db: Session):
    current_time = get_ist_time()

    try:
        # Explicitly update expired (but still UNUSED) codes' status to EXPIRED
        db.query(TwoFACode).filter(
            TwoFACode.expires_at <= current_time,
            TwoFACode.used == TwoFAStatus.UNUSED
        ).update({TwoFACode.used: TwoFAStatus.EXPIRED})

        # Explicitly delete codes marked as EXPIRED or USED
        db.query(TwoFACode).filter(
            TwoFACode.used.in_([TwoFAStatus.EXPIRED, TwoFAStatus.USED])
        ).delete(synchronize_session=False)  # optimize deletion explicitly

        db.commit()

    except Exception as e:
        db.rollback()
        raise e

def update_user_password(db: Session, employee_id: str, hashed_password: str):
    """
    Updates a user's password and last sign-in time
    """
    try:
        current_time = get_ist_time()
        user = db.query(models.User).filter(models.User.employee_id == employee_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # Update the user's password and last sign-in time
        user.password = hashed_password
        user.last_sign_in = current_time

        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while updating user password."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating user password."
        )