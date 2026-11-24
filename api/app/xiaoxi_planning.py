from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PartyType = Literal[
    "solo",
    "couple",
    "friends",
    "family_children",
    "older_adults",
    "unspecified",
]
Pace = Literal["relaxed", "balanced", "rich", "unspecified"]
TransportMode = Literal["walking", "transit", "driving", "taxi"]
SearchCategory = Literal[
    "culture_history",
    "museum_art",
    "nature_scenery",
    "photography",
    "family",
    "food",
    "shopping",
    "nightlife",
    "neighborhood",
    "other",
]


class PlanningIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    city_name: str | None = Field(
        default=None,
        description="用户明确提到的中国目的城市；未提到时必须为 null。",
    )
    day_count: int | None = Field(
        default=None,
        ge=1,
        le=14,
        description="用户明确表达的旅行天数；无法确定时必须为 null。",
    )
    party_type: PartyType = Field(
        default="unspecified",
        description="同行身份，只根据用户原话判断。",
    )
    pace: Pace = Field(
        default="unspecified",
        description="relaxed=轻松，balanced=均衡，rich=紧凑丰富。",
    )
    interests: list[str] = Field(
        default_factory=list,
        max_length=12,
        description="简短、去重的兴趣标签。",
    )
    must_visit_names: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="用户明确指定的必去地点名称。",
    )
    avoid_names: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="用户明确表示不去的地点或类型。",
    )
    dietary_constraints: list[str] = Field(
        default_factory=list,
        max_length=12,
        description="用户明确表达的饮食限制。",
    )
    transport_modes: list[TransportMode] = Field(
        default_factory=list,
        max_length=4,
        description="用户接受的市内交通方式。",
    )
    daily_start_time: str | None = Field(
        default=None,
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
        description="用户明确表达的每日开始时间，24 小时 HH:MM。",
    )
    daily_end_time: str | None = Field(
        default=None,
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
        description="用户明确表达的每日结束时间，24 小时 HH:MM。",
    )
    total_budget_yuan: int | None = Field(
        default=None,
        ge=0,
        le=10_000_000,
        description="用户明确表达的总预算人民币金额。",
    )


class AttractionHypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=80, description="建议交给高德核验的地点名称。")
    category: SearchCategory
    reason: str = Field(
        min_length=1,
        max_length=160,
        description="只说明与用户兴趣/身份/天数的匹配，不声称开放、价格或交通事实。",
    )
    priority: int = Field(ge=1, le=5, description="5 为优先核验，1 为低优先级。")


class PoiSearchTheme(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str = Field(
        min_length=1,
        max_length=40,
        description="适合高德文本检索的简短中文关键词。",
    )
    category: SearchCategory
    reason: str = Field(min_length=1, max_length=160)
    desired_count: int = Field(ge=2, le=20)


class ModelPlanningDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assistant_summary: str = Field(
        min_length=1,
        max_length=400,
        description="用小曦的口吻简洁复述已理解的旅行意图，不承诺最终路线。",
    )
    intent: PlanningIntent
    attraction_hypotheses: list[AttractionHypothesis] = Field(
        default_factory=list,
        max_length=24,
    )
    search_themes: list[PoiSearchTheme] = Field(default_factory=list, max_length=12)
    assumptions: list[str] = Field(default_factory=list, max_length=10)


def unique_text(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            result.append(value)
    return result


def normalized_intent(intent: PlanningIntent) -> PlanningIntent:
    return intent.model_copy(
        update={
            "city_name": intent.city_name.strip() if intent.city_name else None,
            "interests": unique_text(intent.interests),
            "must_visit_names": unique_text(intent.must_visit_names),
            "avoid_names": unique_text(intent.avoid_names),
            "dietary_constraints": unique_text(intent.dietary_constraints),
            "transport_modes": list(dict.fromkeys(intent.transport_modes)),
        }
    )
