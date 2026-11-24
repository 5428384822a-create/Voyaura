"""Add formal itinerary data contracts.

Revision ID: 0014_itinerary_contracts
Revises: 0013_xiaoxi_photo
Create Date: 2026-11-14
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014_itinerary_contracts"
down_revision: str | None = "0013_xiaoxi_photo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "trips",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("client_request_id", sa.Uuid(), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("origin_city_name", sa.String(length=100), nullable=True),
        sa.Column("origin_city_adcode", sa.String(length=12), nullable=True),
        sa.Column("destination_city_name", sa.String(length=100), nullable=False),
        sa.Column("destination_city_adcode", sa.String(length=12), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("day_count", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("party_type", sa.String(length=24), nullable=False),
        sa.Column("pace", sa.String(length=24), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("transport_modes", sa.JSON(), nullable=False),
        sa.Column("dietary_constraints", sa.JSON(), nullable=False),
        sa.Column("total_budget_yuan", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("daily_start_time", sa.Time(), nullable=True),
        sa.Column("daily_end_time", sa.Time(), nullable=True),
        sa.Column("requirements_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "client_request_id", name="uq_trip_user_request"),
    )
    op.create_index(op.f("ix_trips_user_id"), "trips", ["user_id"], unique=False)
    op.create_index(op.f("ix_trips_status"), "trips", ["status"], unique=False)
    op.create_index(
        op.f("ix_trips_destination_city_adcode"),
        "trips",
        ["destination_city_adcode"],
        unique=False,
    )

    op.create_table(
        "trip_days",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("travel_date", sa.Date(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=True),
        sa.Column("theme", sa.String(length=160), nullable=True),
        sa.Column("lodging_area", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("budget_yuan", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("walking_intensity", sa.String(length=20), nullable=False),
        sa.Column("weather_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_id", "day_number", name="uq_trip_day_number"),
    )
    op.create_index(op.f("ix_trip_days_trip_id"), "trip_days", ["trip_id"], unique=False)

    op.create_table(
        "itinerary_stops",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_day_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("poi_id", sa.String(length=64), nullable=True),
        sa.Column("category", sa.String(length=160), nullable=True),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("coordinate_system", sa.String(length=12), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("suggested_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("opening_status", sa.String(length=24), nullable=False),
        sa.Column("opening_hours", sa.String(length=300), nullable=True),
        sa.Column("ticket_price_yuan", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("verification_status", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("source_queried_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["trip_day_id"], ["trip_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "trip_day_id", "sequence", name="uq_itinerary_stop_sequence"
        ),
    )
    op.create_index(
        op.f("ix_itinerary_stops_trip_day_id"),
        "itinerary_stops",
        ["trip_day_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_itinerary_stops_poi_id"), "itinerary_stops", ["poi_id"], unique=False
    )
    op.create_index(
        op.f("ix_itinerary_stops_verification_status"),
        "itinerary_stops",
        ["verification_status"],
        unique=False,
    )

    op.create_table(
        "meal_suggestions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("stop_id", sa.Uuid(), nullable=False),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column("cuisine_tags", sa.JSON(), nullable=False),
        sa.Column("recommended_dishes", sa.JSON(), nullable=False),
        sa.Column("budget_yuan", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("dietary_match", sa.String(length=20), nullable=False),
        sa.Column("reservation_status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stop_id"], ["itinerary_stops.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stop_id", name="uq_meal_suggestion_stop"),
    )
    op.create_index(
        op.f("ix_meal_suggestions_stop_id"),
        "meal_suggestions",
        ["stop_id"],
        unique=False,
    )

    op.create_table(
        "transfer_legs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_day_id", sa.Uuid(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("from_stop_id", sa.Uuid(), nullable=False),
        sa.Column("to_stop_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=True),
        sa.Column("distance_meters", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("walking_distance_meters", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_yuan", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("verification_status", sa.String(length=20), nullable=False),
        sa.Column("queried_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("route_snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["from_stop_id"], ["itinerary_stops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["to_stop_id"], ["itinerary_stops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trip_day_id"], ["trip_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_day_id", "sequence", name="uq_transfer_leg_sequence"),
    )
    op.create_index(
        op.f("ix_transfer_legs_trip_day_id"),
        "transfer_legs",
        ["trip_day_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transfer_legs_from_stop_id"),
        "transfer_legs",
        ["from_stop_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transfer_legs_to_stop_id"),
        "transfer_legs",
        ["to_stop_id"],
        unique=False,
    )

    op.create_table(
        "itinerary_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("stop_id", sa.Uuid(), nullable=True),
        sa.Column("meal_suggestion_id", sa.Uuid(), nullable=True),
        sa.Column("transfer_leg_id", sa.Uuid(), nullable=True),
        sa.Column("evidence_type", sa.String(length=24), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("external_id", sa.String(length=160), nullable=True),
        sa.Column("source_name", sa.String(length=160), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("source_title", sa.String(length=300), nullable=True),
        sa.Column("queried_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence_status", sa.String(length=20), nullable=False),
        sa.Column("value_snapshot", sa.JSON(), nullable=False),
        sa.Column("usage_note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["meal_suggestion_id"], ["meal_suggestions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["stop_id"], ["itinerary_stops.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["transfer_leg_id"], ["transfer_legs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_itinerary_evidence_trip_id"),
        "itinerary_evidence",
        ["trip_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_itinerary_evidence_stop_id"),
        "itinerary_evidence",
        ["stop_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_itinerary_evidence_stop_id"), table_name="itinerary_evidence")
    op.drop_index(op.f("ix_itinerary_evidence_trip_id"), table_name="itinerary_evidence")
    op.drop_table("itinerary_evidence")
    op.drop_index(op.f("ix_transfer_legs_to_stop_id"), table_name="transfer_legs")
    op.drop_index(op.f("ix_transfer_legs_from_stop_id"), table_name="transfer_legs")
    op.drop_index(op.f("ix_transfer_legs_trip_day_id"), table_name="transfer_legs")
    op.drop_table("transfer_legs")
    op.drop_index(op.f("ix_meal_suggestions_stop_id"), table_name="meal_suggestions")
    op.drop_table("meal_suggestions")
    op.drop_index(
        op.f("ix_itinerary_stops_verification_status"), table_name="itinerary_stops"
    )
    op.drop_index(op.f("ix_itinerary_stops_poi_id"), table_name="itinerary_stops")
    op.drop_index(op.f("ix_itinerary_stops_trip_day_id"), table_name="itinerary_stops")
    op.drop_table("itinerary_stops")
    op.drop_index(op.f("ix_trip_days_trip_id"), table_name="trip_days")
    op.drop_table("trip_days")
    op.drop_index(op.f("ix_trips_destination_city_adcode"), table_name="trips")
    op.drop_index(op.f("ix_trips_status"), table_name="trips")
    op.drop_index(op.f("ix_trips_user_id"), table_name="trips")
    op.drop_table("trips")
