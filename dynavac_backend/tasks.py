from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import crud, schemas
from database import get_db
from security import decode_access_token
from jose import JWTError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi import Request


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/attendance", response_model=schemas.AttendanceResponse)
def create_attendance(
        attendance: schemas.AttendanceCreate,
        request: Request,
        db: Session = Depends(get_db),
):
    try:
        # Get token from cookie
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Decode token and extract claims
        payload = decode_access_token(token)
        employee_email = payload.get("sub")
        session_id = payload.get("session_id")
        if not employee_email or not session_id:
            raise HTTPException(status_code=401, detail="Invalid token. User not authorized.")

        # Get employee details and validate session
        user = crud.validate_session_id(db=db, email=employee_email, session_id=session_id)
        if not user:
            # This will catch cases where session_id has been changed/invalidated
            raise HTTPException(status_code=401, detail="Invalid or expired session.")

        # Add additional validation by checking token expiry
        '''if "exp" in payload:
            expiry = datetime.fromtimestamp(payload["exp"])
            if datetime.now(UTC) > expiry:
                raise HTTPException(status_code=401, detail="Token has expired")'''

        # Construct attendance data and proceed
        attendance_data = schemas.AttendanceCreate(
            task_name=attendance.task_name,
            place_of_visit=attendance.place_of_visit,
            purpose_of_visit=attendance.purpose_of_visit,
            visiting_person_name=attendance.visiting_person_name,
            employee_location=attendance.employee_location,
        )

        created_attendance = crud.create_attendance(
            db=db,
            attendance=attendance_data,
            employee_id=user.employee_id,
            designation=user.designation
        )

        return created_attendance
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate token.")

    except SQLAlchemyError as db_error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error occurred")
    except HTTPException as http_error:
        raise http_error
    except ValueError as value_error:
        raise HTTPException(status_code=400, detail=f"Invalid value")
    except TypeError as type_error:
        raise HTTPException(status_code=400, detail=f"Invalid type")
    except AttributeError as attribute_error:
        raise HTTPException(status_code=400, detail=f"Missing attribute")
    except KeyError as key_error:
        raise HTTPException(status_code=400, detail=f"Missing key")
    except FastAPIHTTPException as e:
        # Explicitly re-raise caught HTTPExceptions clearly to maintain specific details.
        raise e
    except Exception as general_error:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")
