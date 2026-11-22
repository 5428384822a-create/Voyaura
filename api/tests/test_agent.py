"""Real workflow/database tests. Explicit provider stubs are not online AMap evidence."""

import copy
import uuid
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.agent.models import AgentRun, SavedArtifact
from app.config import settings
from app.database import Base, get_db
from app.errors import AppError
from app.integrations.amap import AMapClient, AMapPoi, AMapRouteOption, get_amap_client
from app.main import app
from app.models import City, CityMemory, CityVisit, MediaAsset, User

TOKEN = "test-agent-token-not-a-real-secret-0123456789"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


class ExplicitMapStub(AMapClient):
    """Always injected, never installed as a production/default provider."""

    def __init__(self):
        super().__init__(key="")
        self.calls = 0
        self.retry_once = False
        self.invalid_duration = False
        self.invalid_coordinate = False

    def search_pois(self, **kwargs):
        self.calls += 1
        if self.retry_once and self.calls == 1:
            raise AppError("AMAP_RATE_LIMIT", "测试限流", retryable=True)
        items = [
            AMapPoi(
                id=f"TEST{i}",
                name=f"测试地点{i}",
                category="测试",
                typecode="110000",
                address="仅用于测试",
                province="广东省",
                city="广州市",
                district="天河区",
                adcode="440106",
                longitude=(float("nan") if self.invalid_coordinate else 113.3 + i * 0.001),
                latitude=23.1 + i * 0.001,
                opening_hours="09:00-18:00",
            )
            for i in range(4)
        ]
        return items, len(items)

    def plan_route(self, **kwargs):
        self.calls += 1
        return [
            AMapRouteOption(
                distance_meters=2000, duration_seconds=0 if self.invalid_duration else 600, steps=()
            )
        ], None


@dataclass
class Context:
    client: TestClient
    sessions: sessionmaker
    provider: ExplicitMapStub
    owner_id: uuid.UUID
    other_id: uuid.UUID
    city_id: uuid.UUID


@pytest.fixture
def ctx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[Context, None, None]:
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'agent-tests.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)
    with sessions.begin() as db:
        owner = User(username="AuroraRovella", display_name="测试所有者")
        other = User(username="OtherTraveler", display_name="隔离用户")
        city = City(
            adcode="440100",
            name_zh="广州市",
            name_en="Guangzhou",
            province_zh="广东省",
            longitude=113.26,
            latitude=23.12,
        )
        db.add_all([owner, other, city])
        db.flush()
        owner_id, other_id, city_id = owner.id, other.id, city.id

    def database():
        with sessions() as db:
            yield db

    previous = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = database
    provider = ExplicitMapStub()
    app.dependency_overrides[get_amap_client] = lambda: provider
    monkeypatch.setattr(settings, "auth_token", TOKEN)
    monkeypatch.setattr(settings, "auth_username", "AuroraRovella")
    monkeypatch.setenv("VOYAURA_AGENT_LLM_ENABLED", "false")
    try:
        with TestClient(app, headers=HEADERS) as client:
            yield Context(client, sessions, provider, owner_id, other_id, city_id)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
        engine.dispose()


def plan_payload(**updates):
    value = {
        "client_request_id": str(uuid.uuid4()),
        "kind": "plan",
        "goal": "两天轻松旅行",
        "city_adcode": "440100",
        "city_name": "广州市",
        "start_date": "2026-12-01",
        "days": 2,
        "daily_start": "09:00",
        "daily_end": "18:00",
        "budget_yuan": 300,
        "candidates": [
            {
                "name": f"用户提供地点{i}",
                "longitude": 113.3 + 0.003 * i,
                "latitude": 23.1 + 0.002 * i,
                "stay_minutes": 60,
                "opening_start": "09:00",
                "opening_end": "18:00",
                "cost_yuan": 10,
            }
            for i in range(4)
        ],
    }
    value.update(updates)
    return value


def create(ctx: Context, **updates):
    response = ctx.client.post("/api/v1/agent/runs", json=plan_payload(**updates))
    assert response.status_code == 201, response.text
    return response.json()


def confirmation(ctx: Context, run: dict):
    response = ctx.client.post(
        f"/api/v1/agent/runs/{run['id']}/confirmation", json={"expected_revision": run["revision"]}
    )
    assert response.status_code == 200, response.text
    preview = response.json()
    return {
        "expected_revision": run["revision"],
        "confirmation_token": preview["confirmation_token"],
        "content_digest": preview["content_digest"],
        "acknowledge_unverified": True,
    }


def test_local_workflow_persists_real_computation_and_idempotent_save(ctx):
    payload = plan_payload()
    first = ctx.client.post("/api/v1/agent/runs", json=payload).json()
    repeated = ctx.client.post("/api/v1/agent/runs", json=payload).json()
    assert first["id"] == repeated["id"]
    assert first["result"]["verification_status"] == "conditional"
    assert first["result"]["intent_source"] == "local_rules"
    assert len(first["result"]["days"]) == 2
    assert all(c["source"] == "user_provided" for c in first["result"]["candidates"])
    assert any("交通时间未知" in u for u in first["result"]["unknowns"])
    assert ctx.provider.calls == 0
    assert len(first["events"]) >= 5
    assert TOKEN not in str(first)
    body = confirmation(ctx, first)
    path = f"/api/v1/agent/runs/{first['id']}/confirm"
    saved = ctx.client.post(path, json=body)
    again = ctx.client.post(path, json=body)
    assert saved.status_code == again.status_code == 200
    assert saved.json()["status"] == "confirmed"
    assert saved.json()["saved_artifact_id"] == again.json()["saved_artifact_id"]
    with ctx.sessions() as db:
        assert db.scalar(select(func.count()).select_from(SavedArtifact)) == 1
        assert db.scalar(select(func.count()).select_from(CityVisit)) == 0
    assert ctx.client.get(f"/api/v1/agent/runs/{first['id']}").json()["status"] == "confirmed"
    assert ctx.client.get("/api/v1/agent/runs").json()["items"][0]["id"] == first["id"]


def test_empty_provider_stays_needs_input_and_cannot_save(ctx):
    run = create(ctx, candidates=[], allow_external=True, interests=["博物馆"])
    assert run["status"] == "needs_input"
    assert run["result"]["verification_status"] == "information_missing"
    assert any(e.get("details", {}).get("code") == "AMAP_KEY_MISSING" for e in run["events"])
    assert (
        ctx.client.post(
            f"/api/v1/agent/runs/{run['id']}/confirmation", json={"expected_revision": 1}
        ).status_code
        == 409
    )


def test_hard_constraints_are_independently_rejected(ctx):
    run = create(ctx, budget_yuan=1, daily_end="09:30")
    assert run["result"]["verification_status"] == "conflict"
    failed = {x["code"] for x in run["result"]["validation"]["checks"] if x["status"] == "fail"}
    assert {"budget_lower_bound", "daily_end"} <= failed
    assert (
        ctx.client.post(
            f"/api/v1/agent/runs/{run['id']}/confirmation", json={"expected_revision": 1}
        ).status_code
        == 409
    )


def test_edits_invalidate_confirmation_and_can_repair_time_conflict(ctx):
    run = create(ctx, daily_end="09:30")
    path = f"/api/v1/agent/runs/{run['id']}"
    repaired = ctx.client.patch(
        path + "/draft", json={"expected_revision": 1, "daily_end": "18:00"}
    )
    assert repaired.status_code == 200
    assert repaired.json()["revision"] == 2
    old = confirmation(ctx, repaired.json())
    edited = ctx.client.patch(path + "/draft", json={"expected_revision": 2, "title": "已编辑计划"})
    assert edited.status_code == 200
    assert ctx.client.post(path + "/confirm", json=old).status_code == 409
    assert (
        ctx.client.patch(
            path + "/draft", json={"expected_revision": 2, "title": "覆盖"}
        ).status_code
        == 409
    )


def test_confirm_requires_content_token_expiry_and_unknown_ack(ctx):
    run = create(ctx)
    body = confirmation(ctx, run)
    path = f"/api/v1/agent/runs/{run['id']}/confirm"
    no_ack = {**body, "acknowledge_unverified": False}
    assert ctx.client.post(path, json=no_ack).status_code == 422
    assert ctx.client.post(path, json={**body, "content_digest": "0" * 64}).status_code == 409
    assert (
        ctx.client.post(path, json={**body, "confirmation_token": "invalid" * 8}).status_code == 409
    )
    with ctx.sessions.begin() as db:
        row = db.get(AgentRun, uuid.UUID(run["id"]))
        row.confirmation_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    assert ctx.client.post(path, json=body).status_code == 409


def test_identity_isolation_and_request_parameter_conflict(ctx, monkeypatch):
    run = create(ctx)
    monkeypatch.setattr(settings, "auth_username", "OtherTraveler")
    assert ctx.client.get(f"/api/v1/agent/runs/{run['id']}").status_code == 404
    assert ctx.client.get("/api/v1/agent/runs").json()["items"] == []
    assert (
        ctx.client.post(
            f"/api/v1/agent/runs/{run['id']}/confirmation", json={"expected_revision": 1}
        ).status_code
        == 404
    )
    monkeypatch.setattr(settings, "auth_username", "AuroraRovella")
    payload = plan_payload()
    assert ctx.client.post("/api/v1/agent/runs", json=payload).status_code == 201
    payload["goal"] = "修改目标"
    assert ctx.client.post("/api/v1/agent/runs", json=payload).status_code == 409


def test_concurrent_confirmation_writes_one_artifact(ctx):
    run = create(ctx)
    body = confirmation(ctx, run)
    path = f"/api/v1/agent/runs/{run['id']}/confirm"
    with ThreadPoolExecutor(max_workers=2) as workers:
        responses = list(workers.map(lambda _: ctx.client.post(path, json=body), range(2)))
    assert [r.status_code for r in responses] == [200, 200]
    assert len({r.json()["saved_artifact_id"] for r in responses}) == 1
    with ctx.sessions() as db:
        assert db.scalar(select(func.count()).select_from(SavedArtifact)) == 1


def test_explicit_map_stub_retry_success_is_traced_but_not_full_trip_validated(ctx):
    ctx.provider.key = "explicit-test-only"
    ctx.provider.retry_once = True
    run = create(ctx, candidates=[], allow_external=True, interests=["测试主题"])
    assert run["status"] == "awaiting_confirmation"
    assert all(c["source"] == "amap" for c in run["result"]["candidates"])
    assert any(e["status"] == "retrying" for e in run["events"])
    assert any(leg["source"] == "amap" for day in run["result"]["days"] for leg in day["legs"])
    assert run["result"]["verification_status"] == "conditional"
    assert run["result"]["validation"]["unknown_cost_count"] > 0


def test_zero_time_and_nan_coordinates_never_pass_evidence_gate(ctx):
    ctx.provider.key = "explicit-test-only"
    ctx.provider.invalid_duration = True
    run = create(ctx, candidates=[], allow_external=True, interests=["测试"])
    assert all(
        leg["duration_minutes"] is None for day in run["result"]["days"] for leg in day["legs"]
    )
    assert any(
        e.get("details", {}).get("code") == "AMAP_ROUTE_INVALID_EVIDENCE" for e in run["events"]
    )
    ctx.provider.invalid_coordinate = True
    rejected = create(ctx, candidates=[], allow_external=True, interests=["测试"])
    assert rejected["status"] == "needs_input"
    assert rejected["result"]["candidates"] == []


def add_memory(ctx: Context, *, other=False, title="用户真实输入的测试记忆") -> str:
    with ctx.sessions.begin() as db:
        memory = CityMemory(
            user_id=ctx.other_id if other else ctx.owner_id,
            city_id=ctx.city_id,
            title=title,
            body="我在这里写下的一段文字。",
            occurred_at=datetime(2026, 12, 1, 10, tzinfo=UTC),
        )
        db.add(memory)
        db.flush()
        memory_id = memory.id
        for index, scan in enumerate(["clean", "pending"]):
            db.add(
                MediaAsset(
                    memory_id=memory.id,
                    kind="photo",
                    storage_key=f"test/{memory.id}/{index}",
                    original_filename="fixture.jpg",
                    mime_type="image/jpeg",
                    byte_size=100,
                    upload_status="ready",
                    scan_status=scan,
                )
            )
    return str(memory_id)


def test_story_requires_authorization_does_not_invent_sources_or_send_privacy(ctx):
    payload = plan_payload(kind="story", candidates=[])
    assert ctx.client.post("/api/v1/agent/runs", json=payload).status_code == 422
    empty = create(ctx, kind="story", allow_memory_access=True, candidates=[])
    assert empty["status"] == "needs_input"
    assert empty["result"]["story_body"] == ""
    first = add_memory(ctx)
    add_memory(ctx, other=True, title="不得泄露别人的记忆")
    run = create(ctx, kind="story", allow_memory_access=True, candidates=[])
    assert len(run["result"]["source_memories"]) == 1
    assert run["result"]["source_memories"][0]["id"] == first
    assert run["result"]["source_memories"][0]["photo_count"] == 1
    assert "不得泄露" not in str(run)
    assert ctx.provider.calls == 0
    edited = ctx.client.patch(
        f"/api/v1/agent/runs/{run['id']}/draft",
        json={"expected_revision": 1, "story_body": "用户编辑后的故事"},
    ).json()
    assert edited["result"]["edited_by_user"] is True
    body = confirmation(ctx, edited)
    saved = ctx.client.post(f"/api/v1/agent/runs/{run['id']}/confirm", json=body)
    assert saved.status_code == 200
    assert saved.json()["result"]["story_body"] == "用户编辑后的故事"
    with ctx.sessions() as db:
        assert db.scalar(select(func.count()).select_from(CityMemory)) == 2


def test_story_rejects_cross_user_source_and_changed_source_at_confirmation(ctx):
    own = add_memory(ctx)
    other = add_memory(ctx, other=True)
    bad = ctx.client.post(
        "/api/v1/agent/runs",
        json=plan_payload(
            kind="story", allow_memory_access=True, candidates=[], memory_ids=[other]
        ),
    )
    assert bad.status_code == 404
    run = create(ctx, kind="story", allow_memory_access=True, candidates=[], memory_ids=[own])
    body = confirmation(ctx, run)
    with ctx.sessions.begin() as db:
        source = db.get(CityMemory, uuid.UUID(own))
        source.updated_at = datetime.now(UTC) + timedelta(seconds=1)
    response = ctx.client.post(f"/api/v1/agent/runs/{run['id']}/confirm", json=body)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STORY_SOURCES_CHANGED"


@pytest.mark.parametrize(
    "update",
    [
        {"days": 5},
        {"daily_start": "18:00", "daily_end": "09:00"},
        {"allow_model": True, "allow_external": False},
        {"kind": "story", "allow_memory_access": True, "allow_external": True},
        {"candidates": [{"name": "bad", "longitude": 200, "latitude": 23}]},
        {"username": "OtherTraveler"},
    ],
)
def test_invalid_or_privacy_violating_requests_rejected(ctx, update):
    payload = copy.deepcopy(plan_payload())
    payload.update(update)
    response = ctx.client.post("/api/v1/agent/runs", json=payload)
    assert response.status_code in (422, 403)


def test_missing_model_falls_back_with_explicit_evidence(ctx):
    run = create(ctx, allow_external=True, allow_model=True)
    assert run["result"]["intent_source"] == "local_rules"
    assert any(
        e.get("details", {}).get("code") == "MODEL_CONFIGURATION_REQUIRED" for e in run["events"]
    )
