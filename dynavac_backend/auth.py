import uuid
from uuid import uuid4
from fastapi import Request
from fastapi import Response
import fastapi
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import crud, schemas, models
import security
from database import get_db
from schemas import RefreshTokenRequest, ResendVerificationRequest, PasswordResetRequest, PasswordResetVerify
from security import create_access_token, verify_password, create_refresh_token, decode_access_token
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timedelta, UTC
from pytz import timezone
import random
from jose import JWTError
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

# Initialize APIRouter
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Utility function: Get the current IST time
def get_ist_time():
    try:
        ist = timezone("Asia/Kolkata")
        return datetime.now(ist).replace(tzinfo=None)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error in fetching IST time.")


# Generate and send a 2FA code
def generate_and_send_2fa_code(email: str, db: Session):
    try:
        # Generate a 6-digit random code
        code = str(random.randint(100000, 999999))

        # Expiry time for the code (e.g., 5 minutes)
        expires_at = get_ist_time() + timedelta(minutes=5)

        # Save the 2FA code in the database
        two_fa_code = models.TwoFACode(
            email=email,
            code=code,
            created_at=get_ist_time(),
            expires_at=expires_at,
            used=models.TwoFAStatus.UNUSED,
        )
        db.add(two_fa_code)
        db.commit()

        # Here, you would integrate an email service. Simulated with print for now.
        print(f"Verification code sent to {email}: {code}")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while generating 2FA code."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating 2FA code."
        )


# Register endpoint
@router.post("/register")
async def register(user: schemas.UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        # Check if the user is using only Dynavac Mail
        # isDynavacMail = crud.check_dynavac_mail(db, user.email)
        # if not isDynavacMail:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Please use Dynavac mail to register."
        #     )
        # Check if the email already exists in the main credentials table
        existing_user = crud.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )

        # isCorrectEmployeeID = crud.check_dynavac_employee_id(db, user.employee_id)
        # if not isCorrectEmployeeID:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Please use your employee ID to register."
        #     )

        # Check if the employee ID already exists
        existing_user_by_employee_id = crud.get_user_by_employee_id(db, user.employee_id)
        if existing_user_by_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists."
            )

        # Check if the email already exists in pending_users
        pending_user = crud.get_pending_user_by_email(db, user.email)
        if pending_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification already pending for this email. Resend verification if needed."
            )

        # Add the user details to the temporary table (pending_users)
        crud.create_pending_user(db, user)

        try:

            # Generate and send 2FA code to the email
            crud.generate_and_send_2fa_code(user.email, db)

        except Exception as e:
            print(e)

        # Schedule a background task to clean up expired codes
        background_tasks.add_task(update_and_remove_expired_2fa_codes, db)

        return {
            "message": "Verification code sent to your email. Please verify to complete registration."
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during registration."
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise detailed HTTP exceptions here clearly
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )


# Verify registration endpoint
@router.post("/verify-registration")
async def verify_registration(payload: schemas.VerifyRegistrationRequest, db: Session = Depends(get_db)):
    try:
        email, code = payload.email, payload.code
        # Check if the email already exists in the main credentials table
        existing_user = crud.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered."
            )

        # Fetch the 2FA code from the database
        two_fa_code = db.query(models.TwoFACode).filter(
            models.TwoFACode.email == email,
            models.TwoFACode.code == code
        ).first()

        if not two_fa_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code."
            )

        # Check if the code is expired
        if two_fa_code.expires_at < get_ist_time():
            two_fa_code.used = models.TwoFAStatus.EXPIRED  # Mark as expired
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The verification code has expired."
            )

        # Ensure the verification code is unused
        if two_fa_code.used != models.TwoFAStatus.UNUSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The verification code has already been used or expired."
            )

        # Retrieve user details from the pending_users table
        pending_user = crud.get_pending_user_by_email(db, email)
        if not pending_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending registration found for this email."
            )

        # Mark the 2FA code as used and move the user
        two_fa_code.used = models.TwoFAStatus.USED
        db.commit()

        crud.create_user_from_pending(db, pending_user)
        crud.delete_pending_user(db, email)

        return {
            "message": "User verified and successfully registered."
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed due to duplicate data."
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during registration verification."
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration verification."
        )


@router.post("/resend-verification-code")
async def resend_verification_code(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    try:
        # Explicitly cleanup expired codes FIRST
        crud.cleanup_expired_twofa_codes(db)

        # Explicitly verify that the email is pending verification
        pending_user = crud.get_pending_user_by_email(db, request.email)
        if not pending_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="No pending registration found for this email.")

        # Additionally, check if already verified or registered explicitly
        existing_user = crud.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="User already registered.")

        # Explicitly expire existing active codes
        crud.mark_twofa_code_as_expired(db, request.email)

        # Explicitly generate new verification code
        crud.generate_and_send_2fa_code(request.email, db)

        return {"message": "Verification code resent successfully."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Database error")
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Unexpected error")


# Update and remove expired 2FA codes
def update_and_remove_expired_2fa_codes(db: Session):
    try:
        # Get the current IST time
        ist_now = get_ist_time()

        # Update unused codes that have expired
        db.query(models.TwoFACode).filter(
            models.TwoFACode.expires_at < ist_now,
            models.TwoFACode.used == models.TwoFAStatus.UNUSED
        ).update({"used": models.TwoFAStatus.EXPIRED})
        db.commit()

        # Remove expired codes from the database
        db.query(models.TwoFACode).filter(
            models.TwoFACode.used == models.TwoFAStatus.EXPIRED
        ).delete()
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while removing expired codes."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing expired codes."
        )


@router.post("/password-reset-request")
async def password_reset_request(request: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        user = crud.get_user_by_email(db, request.email)
        if not user:
            return {"message": "If the email exists, a reset link will be sent."}

        token = str(uuid4())

        reset_entry = models.PasswordRestToken(
            employee_id=user.employee_id,
            token=token,
            created_at=get_ist_time(),
            expires_at=get_ist_time() + timedelta(minutes=10)
        )
        db.add(reset_entry)
        db.commit()

        reset_link = f"http://localhost:5173/passwordreset?token={token}"

        sub = 'Dynavac Password Reset Request'

        body = f'''Dear {user.email},

You have requested to reset your Dynavac password. Please use the following link to complete the password reset process:

{reset_link}

If you did not request a password reset, please disregard this email and do not reset your password.

Thank you,

Dynavac India Pvt. Ltd.'''

        mail_status = crud.send_email(subject=sub, body=body, to_email=user.email)

        if mail_status:
            return {"message": "If the email exists, a reset link will be sent."}
        else:
            return {"message": "Error in sending email."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while sending password reset link."
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while sending password reset link.")


@router.post("/password-reset")
async def verify_and_reset_password(data: PasswordResetVerify, db: Session = Depends(get_db)):
    try:
        token = data.token
        new_password = data.new_password

        reset_entry = db.query(models.PasswordRestToken).filter(models.PasswordRestToken.token == token).first()
        if not reset_entry or reset_entry.expires_at < get_ist_time():
            return {"message": "Invalid or Expired token."}
        else:
            # user = db.query(models.User).filter(models.User.employee_id == reset_entry.employee_id).first()
            user = crud.get_user_by_employee_id(db, reset_entry.employee_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

        hashed_password = crud.get_password_hash(new_password)

        user.password = hashed_password
        user.last_sign_in = get_ist_time()
        db.commit()

        db.delete(reset_entry)
        db.commit()

        return {"message": "Password reset successful."}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while resetting password." + str(e)
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An unexpected error occurred while resetting password.")


# Login endpoint
@router.post("/login")
async def login(user_login: schemas.UserLogin, response: Response, db: Session = Depends(get_db)):
    try:
        # Retrieve the user by email
        user = crud.get_user_by_email(db, email=user_login.email)
        if not user or not verify_password(user_login.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        # Generate and update session_id
        session_id = crud.update_session_id(db, user)

        # Create tokens
        access_token = create_access_token(user.email, session_id=session_id, expires_delta=timedelta(minutes=15))
        refresh_token = create_refresh_token(user.email, session_id=session_id, expires_delta=timedelta(days=7))

        # Set cookies with HttpOnly attribute
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevent client-side scripts from accessing this cookie
            secure=False,  # Use HTTPS for production
            samesite="Strict"  # Protect against cross-site request forgery (CSRF)
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # Prevent client-side scripts from accessing this cookie
            secure=False,  # Use HTTPS for production
            samesite="Strict"  # Protect against CSRF
        )

        # Return a success message
        return {"message": "Login successful"}

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during login."
        )
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid credentials.")
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login."
        )


# Refresh Token Endpoint
@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    try:
        # Access the refresh token from cookies
        refresh_token_cookie = request.cookies.get("refresh_token")
        if not refresh_token_cookie:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token found.")

        # Decode the refresh token to extract the payload
        payload = decode_access_token(refresh_token_cookie)
        email = payload.get("sub")
        session_id = payload.get("session_id")

        if not email or not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload.")

        # Session validation
        user = crud.validate_session_id(db, email=email, session_id=session_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session.")

        # Rotate session_id on refresh for enhanced security (recommended)
        new_session_id = crud.update_session_id(db, user)

        # Create new tokens
        new_access_token = create_access_token(email, new_session_id, expires_delta=timedelta(minutes=15))
        new_refresh_token = create_refresh_token(email, new_session_id, expires_delta=timedelta(days=7))

        # Set new tokens in cookies
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,  # Prevent client-side scripts from accessing this cookie
            secure=False,  # Use HTTPS for production
            max_age=900,
            samesite="Strict"  # Protect against CSRF
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,  # Prevent client-side scripts from accessing this cookie
            secure=False,  # Use HTTPS for production
            max_age=604800,
            samesite="Strict"  # Protect against CSRF
        )

        # Return a success message
        return {"message": "Tokens refreshed successfully"}

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token.")
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while refreshing token."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while refreshing token."+str(e)
        )


@router.get("/download-attendance-data", response_class=StreamingResponse)
def download_attendance_data(
        request: Request,
        start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
        end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
        db: Session = Depends(get_db)
):
    try:
        # Get access token from HTTP-only cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated."
            )

        # Decode token and get necessary info
        payload = security.decode_access_token(access_token)
        email = payload.get("sub")
        session_id = payload.get("session_id")

        if not email or not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload."
            )

        # Validate session ID against database record
        user = crud.validate_session_id(db=db, email=email, session_id=session_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session."
            )

        # Check token expiry
        '''if "exp" in payload:
            expiry = datetime.fromtimestamp(payload["exp"])
            if datetime.now(UTC) > expiry:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )'''

        # Step 1: Authorize the specific user
        if email != "erp@dynavac.org":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this endpoint."
            )

        elif user.designation != "HR":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this endpoint."
            )

        # Rest of the function remains the same
        # Step 2: Validate date inputs
        try:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d")
            # Adjust to include full time range
            start_datetime = start_date_parsed.replace(hour=0, minute=0, second=0)
            end_datetime = end_date_parsed.replace(hour=23, minute=59, second=59)

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred"+str(e))

    try:
        if start_date_parsed > end_date_parsed:
            raise HTTPException(status_code=400, detail="Start date cannot be greater than end date.")

        # Step 3: Fetch attendance data from the database
        attendance_data = db.query(models.AttendanceData).filter(
            models.AttendanceData.created_at >= start_datetime,
            models.AttendanceData.created_at <= end_datetime
        ).all()

        if not attendance_data:
            raise HTTPException(status_code=404, detail="No attendance records found for the specified range.")

        # Step 4: Convert data to CSV format
        def generate_csv():
            output = StringIO()
            writer = csv.writer(output)

            # Write the header
            writer.writerow(["Task ID", "Employee ID", "Task Name", "Designation", "Place of Visit", "Purpose of Visit",
                             "Visiting Person Name", "Employee Location", "Created At"])

            # Write rows
            for record in attendance_data:
                writer.writerow([
                    record.task_id,
                    record.employee_id,
                    record.task_name,
                    record.designation,
                    record.place_of_visit,
                    record.purpose_of_visit,
                    record.visiting_person_name,
                    record.employee_location,
                    record.created_at
                ])

            output.seek(0)
            yield output.read()
            output.close()

        # Step 5: Create and return a streaming response
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_data_{start_date}_to_{end_date}.csv"}
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error")
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Unexpected error")



# Logout Endpoint
@router.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    try:
        # Get access token from HTTP-only cookie instead of using oauth2_scheme
        access_token = request.cookies.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated."
            )

        # Decode the access token from the HTTP-only cookie
        payload = decode_access_token(access_token)
        email = payload.get("sub")
        session_id = payload.get("session_id")

        if not email or not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload."
            )

        # Validate session_id and user existence
        user = crud.validate_session_id(db, email=email, session_id=session_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session is invalid or already logged out."
            )

        # Invalidate the session by regenerating a new session_id
        crud.update_session_id(db, user)

        # Clear cookies to remove tokens from the client
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return {"detail": "Logged out successfully and session invalidated."}

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during logout."
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during logout."
        )


@router.get("/check-auth")
async def check_auth(request: Request, db: Session = Depends(get_db)):
    try:
        # Retrieve access_token from cookies
        token = request.cookies.get("access_token")
        if not token:
            return {"authenticated": False}

        # Decode the access token
        payload = decode_access_token(token)
        email = payload.get("sub")
        session_id = payload.get("session_id")

        if not email or not session_id:
            return {"authenticated": False}

        # Validate session using CRUD function
        user = crud.validate_session_id(db, email=email, session_id=session_id)
        return {"authenticated": bool(user)}

    except KeyError:
        # Missing fields in token payload
        return {"authenticated": False, "error": "Malformed token payload."}
    except JWTError:
        # Invalid or expired token
        return {"authenticated": False, "error": "Invalid or expired token."}
    except SQLAlchemyError:
        # Database-related errors
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while validating session."
        )
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
        change_password_request: schemas.ChangePasswordRequest,
        request: Request,  # Add request parameter to access cookies
        response: Response,
        db: Session = Depends(get_db)
):
    try:
        # Get token from cookie instead of Authorization header
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Decode the JWT token to get user information
        payload = decode_access_token(token)
        employee_email = payload.get("sub")
        session_id = payload.get("session_id")

        if not employee_email or not session_id:
            raise HTTPException(status_code=401, detail="Invalid token. User not authorized.")

        # Get the user from the database and validate session
        user = crud.validate_session_id(db=db, email=employee_email, session_id=session_id)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session.")

        # Check token expiry
        if "exp" in payload:
            expiry = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > expiry:
                raise HTTPException(status_code=401, detail="Token has expired")

        # Verify the current password
        if not verify_password(change_password_request.current_password, user.password):
            db.rollback()
            raise HTTPException(status_code=400, detail="Current password is incorrect.")

        # Hash the new password
        hashed_password = crud.get_password_hash(change_password_request.new_password)

        # Update the user's password
        updated_user = crud.update_user_password(db=db, employee_id=user.employee_id, hashed_password=hashed_password)
        if not updated_user:
            db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update password.")

        # Generate new tokens after password change with a new session ID
        # This invalidates all existing sessions
        new_session_id = str(uuid.uuid4())

        # Update the session ID in the database
        crud.update_session_id(db=db, user=user)

        # Create new tokens with the new session ID
        access_token = create_access_token(email=employee_email, session_id=new_session_id)
        refresh_token = create_refresh_token(email=employee_email, session_id=new_session_id)

        # Set HTTP-only cookies for both tokens
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Only send over HTTPS
            samesite="lax"  # Provides some CSRF protection
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Only send over HTTPS
            samesite="lax"  # Provides some CSRF protection
        )

        return {"message": "Password changed successfully"}

    except JWTError:
        db.rollback()
        raise HTTPException(status_code=401, detail="Invalid token")
    except SQLAlchemyError as db_error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error occurred during password change.")
    except FastAPIHTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred"+str(e))
