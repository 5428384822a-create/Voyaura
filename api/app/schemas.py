import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.xiaoxi_planning import (
    AttractionHypothesis,
    Pace,
    PartyType,
    PlanningIntent,
    PoiSearchTheme,
    TransportMode,
)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str
    role: str
    is_test_user: bool
    created_at: datetime


class VisitedCityOut(BaseModel):
    adcode: str
    name_zh: str
    name_en: str
    province_zh: str
    longitude: float
    latitude: float
    first_visited_at: datetime
    last_visited_at: datetime
    memory_count: int = 0
    check_in_source: Literal["device", "ip", "manual"] = "device"


class MapStats(BaseModel):
    lit_cities: int
    memories: int
    photos: int
    vlog_minutes: int


class MapYearCityActivity(BaseModel):
    adcode: str
    memory_count: int


class MapYearSummary(BaseModel):
    year: int
    stats: MapStats
    cities: list[MapYearCityActivity]


class MapOverviewOut(BaseModel):
    username: str
    map_center: tuple[float, float]
    default_zoom: float
    stats: MapStats
    visited_cities: list[VisitedCityOut]
    year_summaries: list[MapYearSummary] = Field(default_factory=list)


class CheckInCoordinates(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    accuracy_meters: float | None = Field(default=None, ge=0, le=100_000)
    coordinate_system: Literal["WGS84"] = "WGS84"


class CheckInPreviewOut(BaseModel):
    adcode: str
    city_name: str
    province_name: str
    city_center: tuple[float, float]
    map_position: tuple[float, float]
    formatted_address: str
    accuracy_meters: float | None
    already_lit: bool
    location_source: Literal["device", "ip", "manual"] = "device"
    privacy_notice: str = "仅保存城市中心与到访关系，不保存本次精确定位坐标。"


class CheckInConfirmOut(BaseModel):
    status: Literal["created", "updated"]
    city: VisitedCityOut


class ManualCityCheckIn(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    adcode: str = Field(pattern=r"^\d{6}$")
    city_name: str = Field(min_length=1, max_length=100)
    province_name: str = Field(default="中国", min_length=1, max_length=100)
    longitude: float = Field(ge=73, le=136)
    latitude: float = Field(ge=3, le=54)
    source: Literal["ip", "manual"]


class PoiSearchDraft(BaseModel):
    keywords: str = Field(min_length=1, max_length=80)
    city_adcode: str = Field(pattern=r"^\d{6}$")
    category: str = Field(default="", max_length=80)
    page: int = Field(default=1, ge=1, le=100)
    page_size: int = Field(default=10, ge=1, le=20)


class PoiOut(BaseModel):
    id: str
    name: str
    category: str
    typecode: str
    address: str
    province: str
    city: str
    district: str
    adcode: str
    longitude: float
    latitude: float
    coordinate_system: Literal["GCJ02"] = "GCJ02"
    telephone: str | None = None
    rating: str | None = None
    average_cost: str | None = None
    opening_hours: str | None = None
    navigation_url: str


class PoiSearchOut(BaseModel):
    keywords: str
    city_adcode: str
    total: int
    page: int
    page_size: int
    items: list[PoiOut]
    provider: Literal["amap"] = "amap"
    queried_at: datetime


class PoiDetailOut(BaseModel):
    item: PoiOut
    provider: Literal["amap"] = "amap"
    queried_at: datetime


class RouteCoordinate(BaseModel):
    longitude: float = Field(ge=73, le=136)
    latitude: float = Field(ge=3, le=54)


class LocalRouteDraft(BaseModel):
    mode: Literal["walking", "driving", "transit"]
    origin: RouteCoordinate
    destination: RouteCoordinate
    origin_adcode: str | None = Field(default=None, pattern=r"^\d{6}$")
    destination_adcode: str | None = Field(default=None, pattern=r"^\d{6}$")


class RouteStepOut(BaseModel):
    instruction: str
    distance_meters: int
    duration_seconds: int | None = None
    road_name: str | None = None
    transport: str


class RouteOptionOut(BaseModel):
    distance_meters: int
    duration_seconds: int
    walking_distance_meters: int | None = None
    tolls_yuan: float | None = None
    taxi_cost_yuan: float | None = None
    steps: list[RouteStepOut]


class LocalRouteOut(BaseModel):
    mode: Literal["walking", "driving", "transit"]
    origin: RouteCoordinate
    destination: RouteCoordinate
    coordinate_system: Literal["GCJ02"] = "GCJ02"
    provider: Literal["amap"] = "amap"
    queried_at: datetime
    options: list[RouteOptionOut]


class RouteProviderCapabilityOut(BaseModel):
    mode: Literal["walking", "transit", "driving", "train", "high_speed_rail", "flight"]
    provider: str
    available: bool
    state: Literal["available", "configuration_required", "partner_required"]
    data_scope: list[str]
    application_url: str | None = None
    notice: str


class RouteCapabilitiesOut(BaseModel):
    local: list[RouteProviderCapabilityOut]
    intercity: list[RouteProviderCapabilityOut]
    queried_at: datetime


class XiaoxiPlanningContext(BaseModel):
    city_name: str | None = Field(default=None, min_length=1, max_length=80)
    city_adcode: str | None = Field(default=None, pattern=r"^\d{6}$")
    day_count: int | None = Field(default=None, ge=1, le=14)
    party_type: PartyType | None = None
    pace: Pace | None = None
    interests: list[str] | None = Field(default=None, max_length=12)
    must_visit_names: list[str] | None = Field(default=None, max_length=20)
    avoid_names: list[str] | None = Field(default=None, max_length=20)
    dietary_constraints: list[str] | None = Field(default=None, max_length=12)
    transport_modes: list[TransportMode] | None = Field(default=None, max_length=4)
    daily_start_time: str | None = Field(
        default=None,
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
    )
    daily_end_time: str | None = Field(
        default=None,
        pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
    )
    total_budget_yuan: int | None = Field(default=None, ge=0, le=10_000_000)


class XiaoxiPlanningPreviewDraft(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2_000)
    context: XiaoxiPlanningContext = Field(default_factory=XiaoxiPlanningContext)


class DailyAttractionRange(BaseModel):
    min: int
    max: int


class XiaoxiPlanningCapabilityOut(BaseModel):
    provider: Literal["deepseek"]
    model: str
    available: bool
    state: Literal["available", "configuration_required"]
    structured_output: Literal[True] = True
    notice: str


class XiaoxiPlanningPreviewOut(BaseModel):
    status: Literal["needs_clarification", "ready_for_poi_search"]
    assistant_message: str
    requirements: PlanningIntent
    city_adcode: str | None
    missing_fields: list[str]
    clarification_questions: list[str]
    candidate_target_count: int
    recommended_daily_attractions: DailyAttractionRange
    attraction_hypotheses: list[AttractionHypothesis]
    search_themes: list[PoiSearchTheme]
    assumptions: list[str]
    warnings: list[str]
    provider: Literal["deepseek"]
    model: str
    generated_at: datetime


TripStatus = Literal["draft", "confirmed", "planning", "ready", "archived"]


class TripCreateDraft(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID
    title: str = Field(min_length=1, max_length=160)
    origin_city_name: str | None = Field(default=None, min_length=1, max_length=100)
    origin_city_adcode: str | None = Field(default=None, pattern=r"^\d{6}$")
    destination_city_name: str = Field(min_length=1, max_length=100)
    destination_city_adcode: str = Field(pattern=r"^\d{6}$")
    start_date: date | None = None
    day_count: int = Field(ge=1, le=14)
    timezone: str = Field(default="Asia/Shanghai", min_length=1, max_length=64)
    party_type: PartyType = "unspecified"
    pace: Pace = "unspecified"
    interests: list[str] = Field(default_factory=list, max_length=12)
    transport_modes: list[TransportMode] = Field(default_factory=list, max_length=4)
    dietary_constraints: list[str] = Field(default_factory=list, max_length=12)
    total_budget_yuan: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    daily_start_time: time | None = None
    daily_end_time: time | None = None
    requirements_snapshot: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_daily_window(self) -> "TripCreateDraft":
        if (
            self.daily_start_time is not None
            and self.daily_end_time is not None
            and self.daily_end_time <= self.daily_start_time
        ):
            raise ValueError("daily_end_time must be later than daily_start_time")
        return self


class MealSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stop_id: uuid.UUID
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    cuisine_tags: list[str]
    recommended_dishes: list[str]
    budget_yuan: Decimal | None
    dietary_match: Literal["unknown", "matched", "partial", "conflict"]
    reservation_status: Literal["unknown", "not_required", "recommended", "required"]
    created_at: datetime
    updated_at: datetime


class ItineraryStopOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_day_id: uuid.UUID
    sequence: int
    kind: Literal["attraction", "meal", "lodging", "activity"]
    name: str
    poi_id: str | None
    category: str | None
    address: str | None
    longitude: float | None
    latitude: float | None
    coordinate_system: Literal["GCJ02"] | None
    start_time: time | None
    end_time: time | None
    suggested_duration_minutes: int | None
    opening_status: Literal["unknown", "open", "closed", "needs_verification"]
    opening_hours: str | None
    ticket_price_yuan: Decimal | None
    recommendation_reason: str | None
    verification_status: Literal["unverified", "verified", "ambiguous", "not_found"]
    status: Literal["planned", "confirmed", "skipped"]
    source_queried_at: datetime | None
    meal_suggestion: MealSuggestionOut | None
    created_at: datetime
    updated_at: datetime


class TransferLegOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_day_id: uuid.UUID
    sequence: int
    from_stop_id: uuid.UUID
    to_stop_id: uuid.UUID
    mode: Literal["walking", "transit", "driving", "taxi", "cycling", "train", "flight"]
    provider: str | None
    distance_meters: int | None
    duration_seconds: int | None
    walking_distance_meters: int | None
    estimated_cost_yuan: Decimal | None
    verification_status: Literal["estimated", "verified", "failed"]
    queried_at: datetime | None
    route_snapshot: dict[str, object] | None
    created_at: datetime


class TripDayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    day_number: int
    travel_date: date | None
    title: str | None
    theme: str | None
    lodging_area: str | None
    status: Literal["draft", "planned", "confirmed"]
    start_time: time | None
    end_time: time | None
    budget_yuan: Decimal | None
    walking_intensity: Literal["unknown", "low", "moderate", "high"]
    weather_snapshot: dict[str, object] | None
    stops: list[ItineraryStopOut]
    transfer_legs: list[TransferLegOut]
    created_at: datetime
    updated_at: datetime


class ItineraryEvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trip_id: uuid.UUID
    stop_id: uuid.UUID | None
    meal_suggestion_id: uuid.UUID | None
    transfer_leg_id: uuid.UUID | None
    evidence_type: Literal[
        "poi", "route", "opening_hours", "ticket", "weather", "recommendation"
    ]
    provider: str
    external_id: str | None
    source_name: str
    source_url: str | None
    source_title: str | None
    queried_at: datetime
    confidence_status: Literal["unverified", "verified", "conflicting"]
    value_snapshot: dict[str, object]
    usage_note: str | None
    created_at: datetime


class TripSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    title: str
    status: TripStatus
    origin_city_name: str | None
    origin_city_adcode: str | None
    destination_city_name: str
    destination_city_adcode: str
    start_date: date | None
    end_date: date | None
    day_count: int
    timezone: str
    party_type: PartyType
    pace: Pace
    interests: list[str]
    transport_modes: list[TransportMode]
    total_budget_yuan: Decimal | None
    created_at: datetime
    updated_at: datetime


class TripDetailOut(TripSummaryOut):
    dietary_constraints: list[str]
    daily_start_time: time | None
    daily_end_time: time | None
    requirements_snapshot: dict[str, object]
    confirmed_at: datetime | None
    days: list[TripDayOut]
    evidence: list[ItineraryEvidenceOut]


class TripCreateOut(BaseModel):
    status: Literal["created", "existing"]
    trip: TripDetailOut


class TripListOut(BaseModel):
    items: list[TripSummaryOut]
    total: int
    limit: int
    offset: int


class MediaAssetOut(BaseModel):
    id: uuid.UUID
    kind: Literal["photo", "vlog"]
    original_filename: str
    mime_type: str
    width: int | None
    height: int | None
    duration_seconds: float | None
    visibility: Literal["private"] = "private"
    upload_status: Literal["ready"] = "ready"
    exif_status: Literal["removed", "not_applicable"] = "not_applicable"
    scan_status: Literal["clean", "not_scanned"] = "not_scanned"
    thumbnail_url: str | None = None
    content_url: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    created_at: datetime


class MediaUploadDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID
    kind: Literal["photo", "vlog"]
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=100)
    byte_size: int = Field(gt=0)
    visibility: Literal["private"] = "private"


class MediaUploadPreviewOut(BaseModel):
    kind: Literal["photo", "vlog"]
    filename: str
    mime_type: str
    byte_size: int
    quota_remaining_bytes: int
    visibility: Literal["private"] = "private"
    confirmation_notice: str = (
        "确认后文件将上传到私有对象存储，并在安全扫描后生成预览；照片会移除 EXIF 元数据。"
    )


class MediaUploadIntentOut(BaseModel):
    status: Literal["created", "existing"]
    asset_id: uuid.UUID
    upload_url: str
    method: Literal["PUT"] = "PUT"
    required_headers: dict[str, str]
    expires_at: datetime


class MediaUploadCompleteDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)


class MediaUploadCompleteOut(BaseModel):
    status: Literal["processing", "ready", "existing"]
    asset_id: uuid.UUID
    asset: MediaAssetOut | None = None
    processing_notice: str = "文件已进入私有媒体处理队列，完成安全扫描后才会显示。"


class MediaProcessingStatusOut(BaseModel):
    status: Literal["pending", "processing", "ready", "failed"]
    asset_id: uuid.UUID
    scan_status: Literal["not_scanned", "pending", "scanning", "clean", "infected", "error"]
    failure_code: str | None = None
    failure_message: str | None = None
    retryable: bool = False
    asset: MediaAssetOut | None = None


class MediaTaskOut(BaseModel):
    asset_id: uuid.UUID
    memory_id: uuid.UUID
    memory_title: str
    kind: Literal["photo", "vlog"]
    original_filename: str
    byte_size: int
    upload_status: Literal["pending", "processing", "failed"]
    scan_status: Literal["not_scanned", "pending", "scanning", "clean", "infected", "error"]
    failure_code: str | None = None
    failure_message: str | None = None
    retryable: bool = False
    expired: bool = False
    upload_expires_at: datetime | None = None
    created_at: datetime


class MediaTaskListOut(BaseModel):
    items: list[MediaTaskOut]


class MediaDeleteDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID


class MediaDeletePreviewOut(BaseModel):
    asset_id: uuid.UUID
    memory_id: uuid.UUID
    city_adcode: str
    city_name: str
    memory_title: str
    kind: Literal["photo", "vlog"]
    original_filename: str
    byte_size: int
    upload_status: Literal["pending", "ready", "failed"]
    confirmation_notice: str = "确认后将永久删除原文件、预览图和媒体记录，此操作无法撤销。"


class MediaDeleteConfirmOut(BaseModel):
    status: Literal["deleted", "existing"]
    asset_id: uuid.UUID
    memory_id: uuid.UUID
    city_adcode: str


class CityMemoryItemOut(BaseModel):
    id: uuid.UUID
    title: str
    body: str | None
    occurred_at: datetime
    visibility: Literal["private", "shared"]
    media: list[MediaAssetOut]


class CityMemoryStatsOut(BaseModel):
    memories: int
    photos: int
    vlogs: int
    vlog_minutes: int


class CityMemoryDetailOut(BaseModel):
    city: VisitedCityOut
    visit_note: str | None
    stats: CityMemoryStatsOut
    memories: list[CityMemoryItemOut]


class CityMemoryDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID
    title: str = Field(min_length=1, max_length=160)
    body: str | None = Field(default=None, max_length=5000)
    occurred_at: datetime
    visibility: Literal["private", "shared"] = "private"


class CityMemoryPreviewOut(BaseModel):
    city_adcode: str
    city_name: str
    title: str
    body: str | None
    occurred_at: datetime
    visibility: Literal["private", "shared"]
    confirmation_notice: str = "确认后将把这段文字记忆保存到当前城市档案。"


class CityMemoryConfirmOut(BaseModel):
    status: Literal["created", "existing"]
    memory: CityMemoryItemOut


class CityMemoryUpdatePreviewOut(CityMemoryPreviewOut):
    memory_id: uuid.UUID
    confirmation_notice: str = "确认后将更新这段城市记忆，原内容会被替换。"


class CityMemoryUpdateConfirmOut(BaseModel):
    status: Literal["updated", "existing"]
    memory: CityMemoryItemOut


class CityMemoryDeleteDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID


class CityMemoryDeletePreviewOut(BaseModel):
    memory_id: uuid.UUID
    city_adcode: str
    city_name: str
    title: str
    occurred_at: datetime
    media_count: int
    confirmation_notice: str = "确认后将删除这段记忆及其关联媒体记录，此操作无法撤销。"


class CityMemoryDeleteConfirmOut(BaseModel):
    status: Literal["deleted", "existing"]
    memory_id: uuid.UUID
    city_adcode: str


class ImageStyleRecipeOut(BaseModel):
    version: str
    aspect_ratio: str
    layout: str
    focal_element: str
    typography: str
    color: str
    texture: str
    default_preservation: Literal["balanced", "high"]
    preservation_level: Literal["balanced", "high"] | None = None


class ImageStyleSourceOut(BaseModel):
    name: str
    version: str
    url: str
    license: str


class ImageCaptionOut(BaseModel):
    title: str
    location: str
    date: str
    layout: Literal["archive_band", "postcard_corner", "vertical_stamp"] = "archive_band"
    palette: Literal["coral", "forest", "ink"] = "coral"
    font_style: Literal["sans", "serif"] = "sans"


class XiaoxiPhotoCapabilityOut(BaseModel):
    available: bool
    missing_settings: list[str]
    asset_version: str | None
    positions: list[Literal["left", "right"]]
    scales: list[Literal["small", "medium", "large"]]
    poses: list[str]
    expressions: list[str]


class ImageCompanionOut(BaseModel):
    asset_version: str | None
    pose: str
    expression: str
    position: Literal["left", "right"]
    scale: Literal["small", "medium", "large"]
    method: str
    disclosure: str


class ImageStyleOut(BaseModel):
    id: str
    name: str
    description: str
    swatch: str
    recipe: ImageStyleRecipeOut
    source: ImageStyleSourceOut | None = None


class ImageStyleCatalogOut(BaseModel):
    provider: str
    available: bool
    missing_settings: list[str]
    styles: list[ImageStyleOut]
    companion: XiaoxiPhotoCapabilityOut


class ImageJobDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    source_asset_id: uuid.UUID
    style_id: str = Field(min_length=1, max_length=64)
    prompt: str = Field(default="", max_length=1200)
    negative_prompt: str | None = Field(default=None, max_length=1200)
    preservation_level: Literal["balanced", "high"] = "balanced"
    caption_mode: Literal["none", "travel_stamp"] = "none"
    caption_layout: Literal[
        "archive_band", "postcard_corner", "vertical_stamp"
    ] = "archive_band"
    caption_palette: Literal["coral", "forest", "ink"] = "coral"
    caption_font_style: Literal["sans", "serif"] = "sans"
    companion_enabled: bool = False
    companion_position: Literal["left", "right"] = "right"
    companion_scale: Literal["small", "medium", "large"] = "medium"


class ImageJobCreateDraft(ImageJobDraft):
    client_request_id: uuid.UUID


class ImageJobPreviewOut(BaseModel):
    source_asset_id: uuid.UUID
    source_filename: str
    city_adcode: str
    city_name: str
    memory_id: uuid.UUID
    memory_title: str
    style: ImageStyleOut
    recipe: ImageStyleRecipeOut
    effective_prompt: str
    negative_prompt: str
    preservation_level: Literal["balanced", "high"]
    caption_mode: Literal["none", "travel_stamp"]
    caption: ImageCaptionOut | None = None
    companion: ImageCompanionOut | None = None
    companion_available: bool
    companion_missing_settings: list[str] = Field(default_factory=list)
    provider: str
    provider_available: bool
    confirmation_notice: str = (
        "确认后原图会由私有 worker 发送给已配置的图片 Provider，生成结果仍保存为私有资源。"
    )


class ImageJobOut(BaseModel):
    id: uuid.UUID
    status: Literal["queued", "running", "succeeded", "failed"]
    source_asset_id: uuid.UUID
    source_filename: str
    source_url: str | None = None
    source_thumbnail_url: str | None = None
    city_adcode: str
    city_name: str
    memory_id: uuid.UUID
    memory_title: str
    style_id: str
    provider: str
    provider_job_id: str | None = None
    prompt: str
    negative_prompt: str | None = None
    preservation_level: Literal["balanced", "high"]
    recipe: ImageStyleRecipeOut
    style_source: ImageStyleSourceOut | None = None
    model_names: list[str] = Field(default_factory=list)
    caption_mode: Literal["none", "travel_stamp"]
    caption: ImageCaptionOut | None = None
    companion: ImageCompanionOut | None = None
    is_favorite: bool = False
    output_url: str | None = None
    download_url: str | None = None
    output_mime_type: str | None = None
    output_width: int | None = None
    output_height: int | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    retryable: bool = False
    created_at: datetime
    completed_at: datetime | None = None


class ImageJobCreateOut(BaseModel):
    status: Literal["created", "existing"]
    job: ImageJobOut


class ImageJobListOut(BaseModel):
    items: list[ImageJobOut]


class ImageJobFavoriteDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    favorite: bool


class ImageJobDeleteDraft(BaseModel):
    username: str = Field(default="AuroraRovella", min_length=1, max_length=64)
    client_request_id: uuid.UUID


class ImageJobDeletePreviewOut(BaseModel):
    job_id: uuid.UUID
    source_filename: str
    city_name: str
    memory_title: str
    style: ImageStyleOut
    status: Literal["queued", "running", "succeeded", "failed"]
    has_output: bool
    confirmation_notice: str = "确认后将永久删除生成图和任务记录，原始旅行照片不会被删除。"


class ImageJobDeleteConfirmOut(BaseModel):
    status: Literal["deleted", "existing"]
    job_id: uuid.UUID

