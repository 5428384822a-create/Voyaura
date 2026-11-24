import uuid
from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Literal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="users_username_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    role: Mapped[str] = mapped_column(String(32), default="traveler")
    is_test_user: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    city_visits: Mapped[list["CityVisit"]] = relationship(back_populates="user")
    city_memories: Mapped[list["CityMemory"]] = relationship(back_populates="user")
    trips: Mapped[list["Trip"]] = relationship(back_populates="user")


class City(Base):
    __tablename__ = "cities"
    __table_args__ = (UniqueConstraint("adcode", name="cities_adcode_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    adcode: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name_zh: Mapped[str] = mapped_column(String(100))
    name_en: Mapped[str] = mapped_column(String(100))
    province_zh: Mapped[str] = mapped_column(String(100))
    longitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)

    visits: Mapped[list["CityVisit"]] = relationship(back_populates="city")
    memories: Mapped[list["CityMemory"]] = relationship(back_populates="city")


class CityVisit(Base):
    __tablename__ = "city_visits"
    __table_args__ = (UniqueConstraint("user_id", "city_id", name="uq_city_visit_user_city"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    first_visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_in_source: Mapped[Literal["device", "ip", "manual"]] = mapped_column(
        String(20),
        default="device",
    )

    user: Mapped[User] = relationship(back_populates="city_visits")
    city: Mapped[City] = relationship(back_populates="visits")


class CityMemory(Base):
    __tablename__ = "city_memories"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_city_memory_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"), index=True)
    client_request_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    visibility: Mapped[Literal["private", "shared"]] = mapped_column(
        String(20), default="private"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="city_memories")
    city: Mapped[City] = relationship(back_populates="memories")
    media_assets: Mapped[list["MediaAsset"]] = relationship(
        back_populates="memory",
        cascade="all, delete-orphan",
    )


class MemoryMutation(Base):
    __tablename__ = "memory_mutations"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_memory_mutation_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    target_memory_id: Mapped[uuid.UUID] = mapped_column(index=True)
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    operation: Mapped[str] = mapped_column(String(20))
    payload_hash: Mapped[str] = mapped_column(String(64))
    response_snapshot: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint("client_request_id", name="uq_media_asset_client_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    memory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("city_memories.id", ondelete="CASCADE"),
        index=True,
    )
    kind: Mapped[Literal["photo", "vlog"]] = mapped_column(String(20))
    client_request_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    thumbnail_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    byte_size: Mapped[int] = mapped_column(BigInteger)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    visibility: Mapped[Literal["private"]] = mapped_column(String(20), default="private")
    upload_status: Mapped[Literal["pending", "processing", "ready", "failed"]] = mapped_column(
        String(20), default="ready"
    )
    exif_status: Mapped[Literal["removed", "not_applicable"]] = mapped_column(
        String(24), default="not_applicable"
    )
    scan_status: Mapped[
        Literal["not_scanned", "pending", "scanning", "clean", "infected", "error"]
    ] = mapped_column(String(20), default="not_scanned")
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thumbnail_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thumbnail_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    upload_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    memory: Mapped[CityMemory] = relationship(back_populates="media_assets")


class MediaMutation(Base):
    __tablename__ = "media_mutations"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_media_mutation_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    target_memory_id: Mapped[uuid.UUID] = mapped_column(index=True)
    target_asset_id: Mapped[uuid.UUID] = mapped_column(index=True)
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    operation: Mapped[str] = mapped_column(String(20))
    payload_hash: Mapped[str] = mapped_column(String(64))
    response_snapshot: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ImageGenerationJob(Base):
    __tablename__ = "image_generation_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_image_job_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"))
    memory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("city_memories.id", ondelete="CASCADE"), index=True
    )
    source_asset_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("media_assets.id", ondelete="CASCADE"), index=True
    )
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    provider: Mapped[str] = mapped_column(String(40))
    style_id: Mapped[str] = mapped_column(String(64))
    prompt: Mapped[str] = mapped_column(Text)
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    preservation_level: Mapped[Literal["balanced", "high"]] = mapped_column(
        String(20), default="balanced"
    )
    recipe_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    caption_mode: Mapped[Literal["none", "travel_stamp"]] = mapped_column(
        String(24), default="none"
    )
    caption_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    companion_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[Literal["queued", "running", "succeeded", "failed"]] = mapped_column(
        String(20), default="queued", index=True
    )
    provider_job_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    output_storage_key: Mapped[str | None] = mapped_column(String(512), unique=True, nullable=True)
    output_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    output_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failure_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provider_metadata: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImageJobMutation(Base):
    __tablename__ = "image_job_mutations"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_image_job_mutation_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    target_job_id: Mapped[uuid.UUID] = mapped_column(index=True)
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    operation: Mapped[str] = mapped_column(String(20))
    response_snapshot: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("user_id", "client_request_id", name="uq_trip_user_request"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    client_request_id: Mapped[uuid.UUID] = mapped_column()
    request_fingerprint: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(160))
    status: Mapped[Literal["draft", "confirmed", "planning", "ready", "archived"]] = (
        mapped_column(String(20), default="draft", index=True)
    )
    origin_city_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    origin_city_adcode: Mapped[str | None] = mapped_column(String(12), nullable=True)
    destination_city_name: Mapped[str] = mapped_column(String(100))
    destination_city_adcode: Mapped[str] = mapped_column(String(12), index=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    day_count: Mapped[int] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai")
    party_type: Mapped[str] = mapped_column(String(24), default="unspecified")
    pace: Mapped[str] = mapped_column(String(24), default="unspecified")
    interests: Mapped[list[str]] = mapped_column(JSON, default=list)
    transport_modes: Mapped[list[str]] = mapped_column(JSON, default=list)
    dietary_constraints: Mapped[list[str]] = mapped_column(JSON, default=list)
    total_budget_yuan: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    daily_start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    daily_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    requirements_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship(back_populates="trips")
    days: Mapped[list["TripDay"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripDay.day_number",
    )
    evidence: Mapped[list["ItineraryEvidence"]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
    )


class TripDay(Base):
    __tablename__ = "trip_days"
    __table_args__ = (
        UniqueConstraint("trip_id", "day_number", name="uq_trip_day_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    day_number: Mapped[int] = mapped_column(Integer)
    travel_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    theme: Mapped[str | None] = mapped_column(String(160), nullable=True)
    lodging_area: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[Literal["draft", "planned", "confirmed"]] = mapped_column(
        String(20), default="draft"
    )
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    budget_yuan: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    walking_intensity: Mapped[
        Literal["unknown", "low", "moderate", "high"]
    ] = mapped_column(String(20), default="unknown")
    weather_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    trip: Mapped[Trip] = relationship(back_populates="days")
    stops: Mapped[list["ItineraryStop"]] = relationship(
        back_populates="trip_day",
        cascade="all, delete-orphan",
        order_by="ItineraryStop.sequence",
    )
    transfer_legs: Mapped[list["TransferLeg"]] = relationship(
        back_populates="trip_day",
        cascade="all, delete-orphan",
        order_by="TransferLeg.sequence",
    )


class ItineraryStop(Base):
    __tablename__ = "itinerary_stops"
    __table_args__ = (
        UniqueConstraint("trip_day_id", "sequence", name="uq_itinerary_stop_sequence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trip_days.id", ondelete="CASCADE"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer)
    kind: Mapped[Literal["attraction", "meal", "lodging", "activity"]] = mapped_column(
        String(20)
    )
    name: Mapped[str] = mapped_column(String(200))
    poi_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(160), nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordinate_system: Mapped[Literal["GCJ02"] | None] = mapped_column(
        String(12), nullable=True
    )
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    suggested_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    opening_status: Mapped[
        Literal["unknown", "open", "closed", "needs_verification"]
    ] = mapped_column(String(24), default="unknown")
    opening_hours: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ticket_price_yuan: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    recommendation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[
        Literal["unverified", "verified", "ambiguous", "not_found"]
    ] = mapped_column(String(20), default="unverified", index=True)
    status: Mapped[Literal["planned", "confirmed", "skipped"]] = mapped_column(
        String(20), default="planned"
    )
    source_queried_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    trip_day: Mapped[TripDay] = relationship(back_populates="stops")
    meal_suggestion: Mapped["MealSuggestion | None"] = relationship(
        back_populates="stop",
        cascade="all, delete-orphan",
        uselist=False,
    )


class MealSuggestion(Base):
    __tablename__ = "meal_suggestions"
    __table_args__ = (UniqueConstraint("stop_id", name="uq_meal_suggestion_stop"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("itinerary_stops.id", ondelete="CASCADE"), index=True
    )
    meal_type: Mapped[Literal["breakfast", "lunch", "dinner", "snack"]] = (
        mapped_column(String(20))
    )
    cuisine_tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_dishes: Mapped[list[str]] = mapped_column(JSON, default=list)
    budget_yuan: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    dietary_match: Mapped[Literal["unknown", "matched", "partial", "conflict"]] = (
        mapped_column(String(20), default="unknown")
    )
    reservation_status: Mapped[
        Literal["unknown", "not_required", "recommended", "required"]
    ] = mapped_column(String(20), default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    stop: Mapped[ItineraryStop] = relationship(back_populates="meal_suggestion")


class TransferLeg(Base):
    __tablename__ = "transfer_legs"
    __table_args__ = (
        UniqueConstraint("trip_day_id", "sequence", name="uq_transfer_leg_sequence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_day_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trip_days.id", ondelete="CASCADE"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer)
    from_stop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("itinerary_stops.id", ondelete="CASCADE"), index=True
    )
    to_stop_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("itinerary_stops.id", ondelete="CASCADE"), index=True
    )
    mode: Mapped[
        Literal["walking", "transit", "driving", "taxi", "cycling", "train", "flight"]
    ] = mapped_column(String(20))
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    distance_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    walking_distance_meters: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_yuan: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    verification_status: Mapped[Literal["estimated", "verified", "failed"]] = (
        mapped_column(String(20), default="estimated")
    )
    queried_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    route_snapshot: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    trip_day: Mapped[TripDay] = relationship(back_populates="transfer_legs")


class ItineraryEvidence(Base):
    __tablename__ = "itinerary_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trips.id", ondelete="CASCADE"), index=True
    )
    stop_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("itinerary_stops.id", ondelete="CASCADE"), nullable=True, index=True
    )
    meal_suggestion_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("meal_suggestions.id", ondelete="CASCADE"), nullable=True
    )
    transfer_leg_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("transfer_legs.id", ondelete="CASCADE"), nullable=True
    )
    evidence_type: Mapped[
        Literal[
            "poi",
            "route",
            "opening_hours",
            "ticket",
            "weather",
            "recommendation",
        ]
    ] = mapped_column(String(24))
    provider: Mapped[str] = mapped_column(String(80))
    external_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_name: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    queried_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confidence_status: Mapped[Literal["unverified", "verified", "conflicting"]] = (
        mapped_column(String(20), default="unverified")
    )
    value_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    usage_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    trip: Mapped[Trip] = relationship(back_populates="evidence")

