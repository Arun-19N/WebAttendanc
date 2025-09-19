from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from sqlalchemy.exc import SQLAlchemyError
import tasks
import auth
from database import engine, Base
import logging

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware to allow all origins temporarily for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Create database tables with error handling
try:
    Base.metadata.create_all(bind=engine)
except SQLAlchemyError as e:
    logger.error("Database initialization failed: %s", e)
    raise HTTPException(status_code=500,
                        detail="An error occurred while initializing the database. Please try again later.")

# Include routers
try:
    app.include_router(auth.router)
    app.include_router(tasks.router)
except Exception as e:
    logger.error("Error including routers: %s", e)
    raise HTTPException(status_code=500, detail="An error occurred while setting up routes. Please try again later.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
