"""Fail-closed single-owner access; this is not a multi-tenant account system."""

import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.errors import AppError
from app.models import User
from app.schemas import UserOut

bearer = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/auth", tags=["authentication"])


async def get_actor(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    configured = settings.auth_token
    if len(configured) < 32:
        raise AppError(
            "AUTH_NOT_CONFIGURED",
            "访问令牌未配置。请先初始化本机私有访问凭证。",
            status_code=503,
        )
    if credentials is None or not hmac.compare_digest(
        credentials.credentials.encode("utf-8"), configured.encode("utf-8")
    ):
        raise AppError("AUTH_REQUIRED", "请提供有效的私有访问令牌。", status_code=401)

    actor = db.scalar(select(User).where(User.username == settings.auth_username))
    if actor is None:
        raise AppError("AUTH_ACCOUNT_NOT_FOUND", "访问凭证对应的账户尚未初始化。", status_code=503)
    db.info["actor_id"] = actor.id
    db.info["actor_username"] = actor.username
    for supplied in request.query_params.getlist("username"):
        require_actor_username(db, supplied)
    if "username" in request.path_params:
        require_actor_username(db, str(request.path_params["username"]))
    if request.headers.get("content-type", "").split(";", 1)[0].strip() == "application/json":
        try:
            payload = await request.json()
        except (ValueError, UnicodeDecodeError):
            payload = None  # Leave malformed input to FastAPI's 422 handler.
        if isinstance(payload, dict) and "username" in payload:
            require_actor_username(db, payload["username"])
    request.state.actor_id = actor.id
    return actor


def require_actor_username(db: Session, username: str) -> None:
    """Guard legacy resolvers, including their implicit default username."""
    if db.info.get("actor_username") != username:
        raise AppError("AUTH_FORBIDDEN", "当前凭证无权访问该用户的数据。", status_code=403)


@router.get("/me", response_model=UserOut)
def read_actor(actor: Annotated[User, Depends(get_actor)]) -> User:
    return actor
