from __future__ import annotations

import argparse
import json
import time
from collections.abc import Sequence
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from app.config import settings
from app.errors import AppError
from app.integrations.amap import AMapClient, AMapPoi


def _mapping(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be an object.")
    return cast(dict[str, Any], value)


def _sequence(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{path} must be an array.")
    return cast(list[object], value)


def _text(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-empty string.")
    return value


def _normalize_name(value: str) -> str:
    ignored = " -_()（）·景区风景名胜区杭州店总店"
    return "".join(character for character in value.lower() if character not in ignored)


def _select_poi(items: list[AMapPoi], keywords: str) -> AMapPoi:
    if not items:
        raise ValueError(f"AMap returned no POI for {keywords!r}.")
    normalized_keywords = _normalize_name(keywords)

    def rank(item: AMapPoi) -> tuple[int, int, float, str]:
        normalized_name = _normalize_name(item.name)
        exact = int(normalized_name == normalized_keywords)
        contains = int(
            normalized_keywords in normalized_name or normalized_name in normalized_keywords
        )
        try:
            rating = float(item.rating or 0)
        except ValueError:
            rating = 0
        return (-exact, -contains, -rating, item.id)

    return min(items, key=rank)


def _hydrate_pois(
    client: AMapClient,
    problem: dict[str, Any],
    *,
    queried_at: str,
) -> None:
    places = _sequence(problem.get("places"), "problem.places")
    for index, raw_place in enumerate(places):
        place = _mapping(raw_place, f"problem.places[{index}]")
        keywords = _text(
            place.get("amap_keywords"), f"problem.places[{index}].amap_keywords"
        )
        place_id = _text(place.get("id"), f"problem.places[{index}].id")
        configured_poi_id = place.get("amap_poi_id")
        for attempt in range(4):
            try:
                if configured_poi_id is not None:
                    selected = client.get_poi_detail(
                        _text(
                            configured_poi_id,
                            f"problem.places[{index}].amap_poi_id",
                        )
                    )
                else:
                    items, _ = client.search_pois(
                        keywords=keywords,
                        adcode="330100",
                        page=1,
                        page_size=10,
                    )
                    selected = _select_poi(items, keywords)
                break
            except AppError as exc:
                if exc.retryable and attempt < 3:
                    time.sleep(0.5 * (2**attempt))
                    continue
                raise RuntimeError(
                    f"AMap POI hydration failed for {place_id} ({keywords}): "
                    f"{exc.code}, details={exc.details}"
                ) from exc
        time.sleep(0.25)
        place["longitude"] = selected.longitude
        place["latitude"] = selected.latitude
        place["provider_refs"] = {"amap_poi_id": selected.id}
        place["provider_snapshot"] = {
            "provider": "amap",
            "queried_at": queried_at,
            "matched_name": selected.name,
            "category": selected.category,
            "typecode": selected.typecode,
            "address": selected.address,
            "district": selected.district,
            "adcode": selected.adcode,
            "rating": selected.rating,
            "average_cost": selected.average_cost,
            "opening_hours_raw": selected.opening_hours,
        }


def _report_edge_keys(report: dict[str, Any]) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for algorithm_index, raw_algorithm in enumerate(
        _sequence(report.get("algorithms"), "report.algorithms")
    ):
        algorithm = _mapping(raw_algorithm, f"report.algorithms[{algorithm_index}]")
        if algorithm.get("status") != "feasible":
            continue
        for day_index, raw_day in enumerate(
            _sequence(
                algorithm.get("days", []),
                f"report.algorithms[{algorithm_index}].days",
            )
        ):
            day = _mapping(
                raw_day, f"report.algorithms[{algorithm_index}].days[{day_index}]"
            )
            for leg_index, raw_leg in enumerate(
                _sequence(
                    day.get("legs", []),
                    f"report.algorithms[{algorithm_index}].days[{day_index}].legs",
                )
            ):
                leg_path = (
                    f"report.algorithms[{algorithm_index}].days[{day_index}]"
                    f".legs[{leg_index}]"
                )
                leg = _mapping(raw_leg, leg_path)
                keys.add(
                    (
                        _text(leg.get("from_id"), f"{leg_path}.from_id"),
                        _text(leg.get("to_id"), f"{leg_path}.to_id"),
                        _text(leg.get("mode"), f"{leg_path}.mode"),
                    )
                )
    return keys


def _hydrate_edges(
    client: AMapClient,
    problem: dict[str, Any],
    edge_keys: set[tuple[str, str, str]],
    *,
    queried_at: str,
) -> int:
    places = {
        _text(place.get("id"), f"problem.places[{index}].id"): place
        for index, raw_place in enumerate(
            _sequence(problem.get("places"), "problem.places")
        )
        for place in (_mapping(raw_place, f"problem.places[{index}]"),)
    }
    existing = {
        (
            _text(edge.get("from_id"), f"problem.edges[{index}].from_id"),
            _text(edge.get("to_id"), f"problem.edges[{index}].to_id"),
            _text(edge.get("mode"), f"problem.edges[{index}].mode"),
        ): edge
        for index, raw_edge in enumerate(
            _sequence(problem.get("edges", []), "problem.edges")
        )
        for edge in (_mapping(raw_edge, f"problem.edges[{index}]"),)
    }

    hydrated_count = 0
    for from_id, to_id, mode in sorted(edge_keys):
        current = existing.get((from_id, to_id, mode))
        if (
            current is not None
            and current.get("status") == "verified"
            and current.get("provider") == "amap"
        ):
            continue
        first = places[from_id]
        second = places[to_id]
        for attempt in range(4):
            try:
                options, _ = client.plan_route(
                    mode=mode,
                    origin=(float(first["longitude"]), float(first["latitude"])),
                    destination=(float(second["longitude"]), float(second["latitude"])),
                    origin_adcode="330100",
                    destination_adcode="330100",
                )
                break
            except AppError as exc:
                if exc.retryable and attempt < 3:
                    time.sleep(0.5 * (2**attempt))
                    continue
                raise RuntimeError(
                    f"AMap route hydration failed for {from_id}->{to_id} ({mode}): "
                    f"{exc.code}, details={exc.details}"
                ) from exc
        time.sleep(0.25)
        option = min(options, key=lambda item: item.duration_seconds)
        existing[(from_id, to_id, mode)] = {
            "from_id": from_id,
            "to_id": to_id,
            "mode": mode,
            "duration_minutes": max(1, (option.duration_seconds + 59) // 60),
            "distance_meters": option.distance_meters,
            "status": "verified",
            "provider": "amap",
            "queried_at": queried_at,
        }
        hydrated_count += 1
    problem["edges"] = [existing[key] for key in sorted(existing)]
    return hydrated_count


def hydrate_snapshot(
    source: dict[str, Any],
    client: AMapClient,
    *,
    report: dict[str, Any] | None = None,
    refresh_pois: bool = True,
) -> dict[str, Any]:
    output = deepcopy(source)
    metadata = _mapping(output.get("metadata"), "metadata")
    problem = _mapping(output.get("problem"), "problem")
    queried_at = datetime.now(UTC).isoformat()
    if refresh_pois:
        _hydrate_pois(client, problem, queried_at=queried_at)

    edge_keys = _report_edge_keys(report) if report is not None else set()
    hydrated_edge_count = (
        _hydrate_edges(client, problem, edge_keys, queried_at=queried_at)
        if edge_keys
        else 0
    )
    metadata.update(
        {
            "coordinate_system": "GCJ-02",
            "edge_data_state": (
                "partially_verified_amap_routes"
                if edge_keys
                else "estimated_with_amap_pois"
            ),
            "source_kind": "amap_provider_snapshot_with_experimental_features",
            "queried_at": queried_at,
        }
    )
    notes = list(
        dict.fromkeys(
            _text(item, f"metadata.notes[{index}]")
            for index, item in enumerate(
                _sequence(metadata.get("notes", []), "metadata.notes")
            )
        )
    )
    poi_note = (
        "POI 标识和坐标由高德 Web 服务复核；开放时间、停留时长、费用和效用仍是实验假设。"
    )
    if poi_note not in notes:
        notes.append(poi_note)
    if edge_keys:
        edge_note = (
            f"本轮按实验报告增量查询了 {hydrated_edge_count} 条高德路线；"
            "其余边仍为 estimated。"
        )
        if edge_note not in notes:
            notes.append(edge_note)
    metadata["notes"] = notes
    return output


def _load_json(path: Path) -> dict[str, Any]:
    return _mapping(json.loads(path.read_text(encoding="utf-8")), str(path))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hydrate an optimizer snapshot with AMap POIs and used route edges."
    )
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--reuse-pois",
        action="store_true",
        help="Keep POI IDs and coordinates already stored in the source snapshot.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not settings.amap_web_key:
        raise RuntimeError("VOYAURA_AMAP_WEB_KEY is not configured.")
    source = _load_json(args.source)
    report = _load_json(args.report) if args.report is not None else None
    client = AMapClient(settings.amap_web_key, settings.amap_web_private_key)
    output = hydrate_snapshot(
        source,
        client,
        report=report,
        refresh_pois=not args.reuse_pois,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
