"""Tests unitaires du pipeline pur geodata."""

import json
from pathlib import Path

import pytest

from app.services.geodata_pipeline import (
    assign_region_codes,
    build_count_warning,
    build_unknown_region_warnings,
    dedupe_by_name,
    normalize_names,
    round_coordinates,
    run_pipeline,
    sanitize_properties,
    slugify,
)


def _square(lat: float, lon: float, name: str, level: str = "4", d: float = 0.4) -> dict:
    coords = [
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
    ]
    return {
        "type": "Feature",
        "properties": {"name": name, "admin_level": level},
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


@pytest.fixture
def tmp_geojson_23(tmp_path: Path) -> Path:
    feats = [
        _square(-18.9 + i * 0.5, 47.5, f"Region{i}", "4") for i in range(23)
    ]
    fc = {"type": "FeatureCollection", "features": feats}
    p = tmp_path / "in.geojson"
    p.write_text(json.dumps(fc))
    return p


def test_pipeline_filters_admin_level(tmp_path: Path):
    feats = [
        _square(-18, 47, "Keep", "4"),
        _square(-19, 47, "Drop", "6"),
    ]
    p = tmp_path / "in.geojson"
    p.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    res = run_pipeline(
        p,
        aliases={},
        region_code_prefix="MG-",
        simplify_ratio=0.04,
        min_feature_area_deg2=0.001,
        coordinate_precision=4,
        expected_min=1,
        expected_max=100,
    )
    names = [f["properties"]["name"] for f in res.features]
    assert names == ["Keep"]


def test_dedupe_keeps_largest():
    a = _square(-18, 47, "Same", d=0.1)
    b = _square(-18, 47, "Same", d=0.5)
    out, warns = dedupe_by_name([a, b])
    assert len(out) == 1
    assert any(w["code"] == "DUPLICATE_NAME_DROPPED" for w in warns)


def test_normalize_alias_matsiatra():
    feats = [_square(-21.5, 47, "Matsiatra Ambony")]
    out = normalize_names(feats, {"matsiatra ambony": "Haute Matsiatra"})
    assert out[0]["properties"]["name"] == "Haute Matsiatra"


def test_slugify_nfd():
    assert slugify("Amoron'i Mania") == "amoron-i-mania"
    assert slugify("Vohémar") == "vohemar"


def test_assign_region_code():
    feats = [_square(-21.5, 47, "Haute Matsiatra")]
    out = assign_region_codes(feats, "MG-")
    assert out[0]["properties"]["region_code"] == "MG-haute-matsiatra"


def test_sanitize_strips_html_and_unknown():
    feat = {
        "type": "Feature",
        "properties": {
            "name": "X",
            "admin_level": "4",
            "evil": "<script>alert(1)</script>",
            "iso": "MG",
        },
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
    }
    out = sanitize_properties([feat])
    assert set(out[0]["properties"].keys()) <= {
        "name",
        "name_official",
        "region_code",
        "admin_level",
    }


def test_round_coordinates_4_decimals():
    feat = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[1.123456, 2.987654], [3.0, 4.0]]],
        },
    }
    out = round_coordinates([feat], 4)
    assert out[0]["geometry"]["coordinates"][0][0] == [1.1235, 2.9877]


def test_count_warning_out_of_range():
    w = build_count_warning(31, 20, 30)
    assert w and w["code"] == "FEATURE_COUNT_OUT_OF_RANGE"
    assert build_count_warning(25, 20, 30) is None


def test_unknown_region_warning():
    feats = [{"properties": {"name": "Foobar"}}]
    warns = build_unknown_region_warnings(feats, {"analamanga"})
    assert warns and warns[0]["code"] == "REGION_NOT_IN_DATABASE"


def test_pipeline_produces_region_names_and_geojson(tmp_geojson_23: Path):
    res = run_pipeline(
        tmp_geojson_23,
        aliases={},
        region_code_prefix="MG-",
        simplify_ratio=0.04,
        min_feature_area_deg2=0.001,
        coordinate_precision=4,
        expected_min=20,
        expected_max=30,
    )
    assert len(res.features) == 23
    assert len(res.region_names) == 23
    assert res.geojson["type"] == "FeatureCollection"
    assert res.processed_size_bytes > 0
