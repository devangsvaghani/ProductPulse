from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database.session import engine
from database.models import Base
from api.v1 import uploads, auth, admin
from core.logging_config import setup_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This function runs on application startup and shutdown
    setup_logging()
    logger.info("Application startup...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables checked/created.")
    yield # The application runs while the server is active
    logger.info("Application shutdown.")


app = FastAPI(title="ProductPulse API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the ProductPulse API!"}