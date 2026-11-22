import pytest

from app.errors import AppError
from app.integrations.amap import AMapClient


@pytest.mark.parametrize("location", ["nan,23", "113,inf", "181,23", "113,-91", "", "0"])
def test_map_provider_invalid_coordinates_are_rejected(location: str) -> None:
    with pytest.raises(AppError, match="坐标") as result:
        AMapClient._parse_location(location)
    assert result.value.code == "AMAP_COORDINATE_INVALID"


@pytest.mark.parametrize(
    "payload",
    [
        {"distance": "100"},
        {"distance": "100", "duration": "nan"},
        {"distance": "100", "duration": "-1"},
        {"distance": "100", "duration": "0"},
        {"distance": "inf", "duration": "10"},
    ],
)
def test_unknown_or_invalid_duration_never_becomes_zero(payload: dict) -> None:
    with pytest.raises(AppError) as result:
        AMapClient._route_option_from_payload(payload, mode="walking", route={})
    assert result.value.code == "AMAP_ROUTE_DATA_INCOMPLETE"
