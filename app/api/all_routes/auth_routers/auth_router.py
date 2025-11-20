from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db
from app.api.all_routes.auth_routers.schemas.auth_io import RegisterIn, LoginIn, RefreshIn, AuthTokensOut, UserOut
from app.auth.services.auth_service import register as svc_register, login as svc_login, refresh as svc_refresh, logout as svc_logout
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def auth_health(session: AsyncSession = Depends(get_db)):
    """Check database connectivity for auth services."""
    try:
        await session.execute(text("SELECT 1"))
        return {"db": "ok"}
    except Exception as exc:
        logger.error("Auth DB health check failed", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"db": "down", "error": str(exc)},
        )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterIn, session: AsyncSession = Depends(get_db)) -> UserOut:
    """Register a new user."""
    try:
        user = await svc_register(session, payload.username, payload.password)
        await session.commit()
        return user
    except ValueError as e:
        msg = str(e)
        if "exists" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        if "Password" in msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")
        raise
    except Exception:
        await session.rollback()
        logger.exception("Unhandled error during /auth/register")
        raise


@router.post("/login", response_model=AuthTokensOut)
async def login(payload: LoginIn, session: AsyncSession = Depends(get_db)) -> AuthTokensOut:
    """Login a user and return access and refresh tokens."""
    try:
        access, refresh = await svc_login(session, payload.username, payload.password)
        await session.commit()
        return AuthTokensOut(access_token=access, refresh_token=refresh)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    except Exception:
        await session.rollback()
        logger.exception("Unhandled error during /auth/login")
        raise


@router.post("/refresh", response_model=AuthTokensOut)
async def refresh(payload: RefreshIn, session: AsyncSession = Depends(get_db)) -> AuthTokensOut:
    """Refresh a refresh token and return new access and refresh tokens."""
    try:
        access, refresh_token = await svc_refresh(session, payload.refresh_token)
        await session.commit()
        return AuthTokensOut(access_token=access, refresh_token=refresh_token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    except Exception:
        await session.rollback()
        logger.exception("Unhandled error during /auth/refresh")
        raise


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshIn, session: AsyncSession = Depends(get_db)) -> None:
    """Logout a user and revoke the refresh token."""
    try:
        await svc_logout(session, payload.refresh_token)
        await session.commit()
    except Exception:
        await session.rollback()
        logger.exception("Unhandled error during /auth/logout")
        raise


@router.get("/me", response_model=UserOut)
async def me(current_user = Depends(get_current_user)) -> UserOut:  
    """Get the current user."""
    return current_user
