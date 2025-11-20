import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.all_routes import all_imports
from api.lifecycle import startup as lifecycle_startup  # local package
from api.kafka.client import EngineOverloadedError

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger(__name__)

application = FastAPI(title="FunctionLab API")

# ---------- CORS – Allow UI dev server ----------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Rate limiting ----------
limiter = Limiter(key_func=get_remote_address)
application.state.limiter = limiter
application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------- Exception handlers ----------
@application.exception_handler(EngineOverloadedError)
async def engine_overloaded_exception_handler(
    request: Request,
    exc: EngineOverloadedError,
) -> HTTPException:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="The server is busy. Please try again later.",
    ) from exc

# ---------- Routers ----------
for r in all_imports.routers:
    application.include_router(r)

# ---------- Lifecycle ----------
@application.on_event("startup")
async def _startup():
    await lifecycle_startup.on_startup(application)


@application.on_event("shutdown")
async def _shutdown():
    await lifecycle_startup.on_shutdown(application)

# ---------- Basic routes ----------
@application.get("/")
async def root():
    return {"message": "FunctionLab API"}


@application.get("/health")
async def health():
    return {"status": "ok"}

app = application
