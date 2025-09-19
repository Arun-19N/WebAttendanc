from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import JWT_SECRET
from fastapi import HTTPException, status
from pytz import timezone
import logging

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


# Utility function to get the current IST time
def get_ist_time():
    try:
        ist = timezone('Asia/Kolkata')
        #current_time = datetime.now(ist).replace(tzinfo=None)  # Compute the current IST time
        #print(f"Current IST time: {current_time}")  # Log the current time without recursion
        return datetime.now(ist).replace(tzinfo=None)
    except Exception as e:
        logging.error(f"Error getting IST time: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing IST time."
        )


# Function to verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logging.error(f"Error verifying password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying password."
        )


# Function to hash a password
def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logging.error(f"Error hashing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error hashing password."
        )


# Function to create a JWT access token
def create_access_token(email: str, session_id: str, expires_delta: timedelta = None) -> str:
    try:
        if expires_delta:
            #print(f"Access token expiration set to: {expires_delta}")
            expire = get_ist_time() + expires_delta
        else:
            #print("Default expiration of 15 minutes applied to access token.")
            expire = get_ist_time() + timedelta(minutes=15)
        payload = {
            "sub": email,
            "session_id": session_id,
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return encoded_jwt

    except Exception as e:
        logging.error(f"Error creating access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating access token."
        )


# Function to decode a JWT token and return the payload
def decode_access_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = payload.get("sub")
        session_id = payload.get("session_id")

        if not email or not session_id:
            raise HTTPException(status_code=401, detail="Invalid token payload structure.")

        return payload
    except JWTError as e:
        logging.error(f"JWT decoding error: {str(e)}")
        raise credentials_exception
    except KeyError as e:
        logging.error(f"KeyError: {str(e)}")
    except Exception as e:
        logging.error(f"Error decoding access token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error decoding access token."
        )


# Function to create a JWT refresh token
def create_refresh_token(email: str, session_id: str, expires_delta: timedelta = None) -> str:
    """Create a refresh token with a longer expiration time."""
    try:
        expire = get_ist_time() + (expires_delta or timedelta(days=7))  # Default: 7 days
        payload = {
            "sub": email,
            "session_id": session_id,
            "exp": expire
        }
        encoded_jwt = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        logging.error(f"Error creating refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating refresh token."
        )
