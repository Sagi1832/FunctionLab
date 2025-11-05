import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from . import all_imports
from app.config.settings import settings



logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FunctionLab API")

limiter = new_limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
CORS_ORIGINS = getattr(settings, "cors_origins_list", ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
async def startup_event():
    """Log environment configuration at startup."""
    env_db_url = os.getenv("DATABASE_URL", "NOT SET")
    if env_db_url != "NOT SET":
        masked = env_db_url
        if "@" in masked and ":" in masked.split("@")[0]:
            parts = masked.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                if len(user_pass) == 2:
                    masked = f"{user_pass[0]}:***@{parts[1]}"
        logger.info(f"Environment DATABASE_URL (masked): {masked}")
    else:
        logger.warning("DATABASE_URL not found in environment variables")
    
    # Also log what settings sees
    try:
        from app.config.settings import settings
        from app.db.session import _mask_password
        logger.info(f"Settings.DATABASE_URL will be used (masked): {_mask_password(settings.DATABASE_URL)}")
    except Exception as e:
        logger.error(f"Error reading settings.DATABASE_URL: {e}")

@app.get("/")
async def root():
    return {"message": "FunctionLab API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/db")
async def health_db():
    """Test database connection."""
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                return {"status": "ok", "database": "connected"}
        return {"status": "error", "message": "Query returned unexpected result"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}, 500

for r in all_imports.routers:
    app.include_router(r)
