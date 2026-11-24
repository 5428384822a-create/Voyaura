from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.integrations.travel_llm import (
    TravelPlanningExtractor,
    get_travel_planning_extractor,
)
from app.schemas import (
    DailyAttractionRange,
    XiaoxiPlanningCapabilityOut,
    XiaoxiPlanningContext,
    XiaoxiPlanningPreviewDraft,
    XiaoxiPlanningPreviewOut,
)
from app.xiaoxi_planning import PlanningIntent, normalized_intent

router = APIRouter(prefix="/xiaoxi/planning", tags=["xiaoxi-planning"])


def _merge_confirmed_context(
    intent: PlanningIntent,
    context: XiaoxiPlanningContext,
) -> PlanningIntent:
    updates: dict[str, object] = {}
    for field_name in (
        "city_name",
        "day_count",
        "party_type",
        "pace",
        "interests",
        "must_visit_names",
        "avoid_names",
        "dietary_constraints",
        "transport_modes",
        "daily_start_time",
        "daily_end_time",
        "total_budget_yuan",
    ):
        value = getattr(context, field_name)
        if value is not None:
            updates[field_name] = value
    return normalized_intent(intent.model_copy(update=updates))


def _missing_fields(intent: PlanningIntent) -> list[str]:
    missing = []
    if not intent.city_name:
        missing.append("city_name")
    if intent.day_count is None:
        missing.append("day_count")
    return missing


def _clarification_questions(missing_fields: list[str]) -> list[str]:
    questions = {
        "city_name": "你想去哪个城市旅行？",
        "day_count": "这次计划安排几天？",
    }
    return [questions[field] for field in missing_fields]


@router.get("/capability", response_model=XiaoxiPlanningCapabilityOut)
def get_planning_capability(
    extractor: Annotated[TravelPlanningExtractor, Depends(get_travel_planning_extractor)],
) -> XiaoxiPlanningCapabilityOut:
    return XiaoxiPlanningCapabilityOut(
        provider=extractor.provider,
        model=extractor.model,
        available=extractor.available,
        state="available" if extractor.available else "configuration_required",
        notice=(
            "DeepSeek 已配置，可生成结构化需求和待高德核验的候选搜索计划。"
            if extractor.available
            else "需要在 API 环境配置 VOYAURA_DEEPSEEK_API_KEY。"
        ),
    )


@router.post("/preview", response_model=XiaoxiPlanningPreviewOut)
def preview_planning_request(
    payload: XiaoxiPlanningPreviewDraft,
    extractor: Annotated[TravelPlanningExtractor, Depends(get_travel_planning_extractor)],
) -> XiaoxiPlanningPreviewOut:
    context_payload = payload.context.model_dump(exclude_none=True)
    model_draft = extractor.extract(payload.message.strip(), context_payload)
    intent = _merge_confirmed_context(model_draft.intent, payload.context)
    missing_fields = _missing_fields(intent)
    ready = not missing_fields
    day_count = intent.day_count or 1
    candidate_target_count = max(12, min(80, day_count * 10)) if ready else 0
    daily_range = {
        "relaxed": (2, 3),
        "balanced": (3, 4),
        "rich": (4, 5),
        "unspecified": (3, 4),
    }[intent.pace]

    hypotheses = model_draft.attraction_hypotheses if ready else []
    search_themes = model_draft.search_themes if ready else []
    return XiaoxiPlanningPreviewOut(
        status="ready_for_poi_search" if ready else "needs_clarification",
        assistant_message=model_draft.assistant_summary,
        requirements=intent,
        city_adcode=payload.context.city_adcode,
        missing_fields=missing_fields,
        clarification_questions=_clarification_questions(missing_fields),
        candidate_target_count=candidate_target_count,
        recommended_daily_attractions=DailyAttractionRange(
            min=daily_range[0],
            max=daily_range[1],
        ),
        attraction_hypotheses=hypotheses,
        search_themes=search_themes,
        assumptions=model_draft.assumptions,
        warnings=[
            "模型建议仅用于候选检索，不代表地点已存在或适合最终行程。",
            "坐标、开放时间、门票和交通耗时必须由高德或官方来源核验。",
            "区域分组和每日路线必须经过独立优化器与可行性验证器。",
        ],
        provider=extractor.provider,
        model=extractor.model,
        generated_at=datetime.now(UTC),
    )
