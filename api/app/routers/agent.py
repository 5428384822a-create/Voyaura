import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.models import AgentRun
from app.agent.schemas import (
    ConfirmationOut,
    ConfirmationRequest,
    ConfirmRequest,
    DraftEdit,
    RunCreate,
    RunOut,
)
from app.agent.service import (
    confirm_run,
    create_run,
    edit_run,
    get_run,
    out,
    prepare_confirmation,
    recover_run,
)
from app.agent.tools import AgentSettings
from app.auth import get_actor
from app.database import get_db
from app.integrations.amap import AMapClient, get_amap_client
from app.models import User

router = APIRouter(prefix="/agent", tags=["xiaoxi-agent"])
Db = Annotated[Session, Depends(get_db)]
Actor = Annotated[User, Depends(get_actor)]
MapClient = Annotated[AMapClient, Depends(get_amap_client)]


@router.get("/capabilities")
def capabilities(actor: Actor, client: MapClient) -> dict:
    settings = AgentSettings()
    return {
        "amap_configured": bool(client.key),
        "model_configured": bool(settings.llm_enabled and settings.llm_api_key),
        "intent_default": "local_rules",
        "privacy_notice": "默认不调用外部服务。旅行故事只在本地整理当前用户明确授权的记录。",
        "limits": {"days": 4, "candidates": 12, "search_topics": 3, "attempts": 2},
        "tools": [
            "amap.search_poi",
            "amap.get_route",
            "memory.read_authorized",
            "day_planner",
            "independent_validator",
            "deepseek.extract_search_topics",
        ],
    }


@router.post("/runs", response_model=RunOut, status_code=201)
def start_run(payload: RunCreate, db: Db, actor: Actor, client: MapClient) -> RunOut:
    return out(db, create_run(db, actor, payload, client))


@router.get("/runs")
def list_runs(db: Db, actor: Actor, limit: Annotated[int, Query(ge=1, le=20)] = 20) -> dict:
    runs = db.scalars(
        select(AgentRun)
        .where(AgentRun.user_id == actor.id)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
    ).all()
    for run in runs:
        recover_run(db, run)
    return {"items": [out(db, run) for run in runs]}


@router.get("/runs/{run_id}", response_model=RunOut)
def read_run(run_id: uuid.UUID, db: Db, actor: Actor) -> RunOut:
    return out(db, get_run(db, actor, run_id))


@router.patch("/runs/{run_id}/draft", response_model=RunOut)
def update_draft(run_id: uuid.UUID, payload: DraftEdit, db: Db, actor: Actor) -> RunOut:
    return out(db, edit_run(db, actor, run_id, payload))


@router.post("/runs/{run_id}/confirmation", response_model=ConfirmationOut)
def preview_confirmation(
    run_id: uuid.UUID, payload: ConfirmationRequest, db: Db, actor: Actor
) -> dict:
    return prepare_confirmation(db, actor, get_run(db, actor, run_id), payload.expected_revision)


@router.post("/runs/{run_id}/confirm", response_model=RunOut)
def save_confirmation(run_id: uuid.UUID, payload: ConfirmRequest, db: Db, actor: Actor) -> RunOut:
    return out(db, confirm_run(db, actor, get_run(db, actor, run_id), payload))
