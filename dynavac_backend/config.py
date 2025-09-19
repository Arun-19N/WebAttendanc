import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    #DATABASE_URL = "default_database_url"
    exit()

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.error("JWT_SECRET is not set in the environment variables.")
    #JWT_SECRET = "default_jwt_secret"
    exit()

EMAIL_SENDER  = os.getenv("EMAIL_ADDRESS")
if not EMAIL_SENDER:
    logger.error("EMAIL_ADDRESS is not set in the environment variables.")
    #Email_SENDER = "default_email_address"
    exit()

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
if not EMAIL_PASSWORD:
    logger.error("EMAIL_PASSWORD is not set in the environment variable.")

SMTP_SERVER = os.getenv("SMTP_SERVER")
if not SMTP_SERVER:
    logger.error("SMTP_SERVER is not set in the environment variable.")

SMTP_PORT = os.getenv("SMTP_PORT")
if not SMTP_PORT:
    logger.error("SMTP_PORT is not set in the environment variable.")

