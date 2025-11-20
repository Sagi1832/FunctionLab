# app/main.py
import asyncio
import logging

from app.api.all_routes.routes import app
from engine.workers.runtime import run_worker
from fastapi.middleware.cors import CORSMiddleware  # ← חדש

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_engine_worker() -> None:
    """
    Start the Kafka engine worker loop when the engine container starts.
    This runs `run_worker()` as a background task on the same event loop
    that FastAPI/Uvicorn use.
    """
    logger.info("Starting engine Kafka worker loop in background...")
    asyncio.create_task(run_worker())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
