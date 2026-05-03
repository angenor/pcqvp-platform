"""Pure pipeline pour traitement GeoJSON régional.

Toutes les fonctions sont pures (aucun side-effect, aucune mutation des entrées),
prennent des structures dict/list et retournent de nouvelles structures.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import ijson
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.geometry.polygon import orient as orient_polygon
from shapely.validation import make_valid

try:
    from simplification.cutil import simplify_coords_vw
except Exception:  # pragma: no cover - fallback if C ext missing
    simplify_coords_vw = None  # type: ignore


Feature = dict[str, Any]
Warning = dict[str, Any]
ALLOWED_PROPS = {"name", "name_official", "region_code", "admin_level"}


@dataclass(frozen=True)
class PipelineResult:
    features: list[Feature]
    region_names: list[str]
    warnings: list[Warning] = field(default_factory=list)
    geojson: dict[str, Any] = field(default_factory=dict)
    processed_size_bytes: int = 0


def _norm(name: str) -> str:
    n = unicodedata.normalize("NFD", name)
    return "".join(c for c in n if unicodedata.category(c) != "Mn").lower().strip()


def slugify(name: str) -> str:
    n = unicodedata.normalize("NFD", name)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn").lower()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n


def parse_streaming(file_path: str | Path) -> Iterator[Feature]:
    """Parse streaming d'un GeoJSON. Yield features admin_level=='4' avec name."""
    with open(file_path, "rb") as fh:
        for feat in ijson.items(fh, "features.item"):
            if not isinstance(feat, dict):
                continue
            props = feat.get("properties") or {}
            name = (props.get("name") or "").strip()
            admin_level = str(props.get("admin_level") or "")
            geom = feat.get("geometry") or {}
            gtype = geom.get("type")
            if not name:
                continue
            if admin_level != "4":
                continue
            if gtype not in ("Polygon", "MultiPolygon"):
                continue
            yield feat


def _feature_area(feat: Feature) -> float:
    try:
        g = shape(feat["geometry"])
        return float(abs(g.area))
    except Exception:
        return 0.0


def dedupe_by_name(
    features: Iterable[Feature],
) -> tuple[list[Feature], list[Warning]]:
    """Garde la feature ayant la plus grande aire pour chaque nom normalisé."""
    by_key: dict[str, Feature] = {}
    warnings: list[Warning] = []
    for f in features:
        key = _norm((f.get("properties") or {}).get("name", ""))
        if key not in by_key:
            by_key[key] = f
            continue
        prev = by_key[key]
        prev_area = _feature_area(prev)
        cur_area = _feature_area(f)
        kept = f if cur_area > prev_area else prev
        dropped = prev if kept is f else f
        by_key[key] = kept
        warnings.append(
            {
                "code": "DUPLICATE_NAME_DROPPED",
                "message": (
                    f"Duplicate '{(dropped.get('properties') or {}).get('name')}' "
                    "— kept feature with largest area"
                ),
                "details": {
                    "name": (kept.get("properties") or {}).get("name"),
                    "kept_area_deg2": round(max(prev_area, cur_area), 6),
                },
            }
        )
    return list(by_key.values()), warnings


def normalize_names(
    features: Iterable[Feature], aliases: dict[str, str]
) -> list[Feature]:
    """Applique la table d'alias (clé normalisée) sur properties.name."""
    aliases_norm = {_norm(k): v for k, v in (aliases or {}).items()}
    out: list[Feature] = []
    for f in features:
        props = dict(f.get("properties") or {})
        original = (props.get("name") or "").strip()
        canonical = aliases_norm.get(_norm(original), original)
        props["name"] = canonical
        if "name_official" not in props or not props.get("name_official"):
            props["name_official"] = canonical
        out.append({**f, "properties": props})
    return out


def assign_region_codes(
    features: Iterable[Feature], prefix: str
) -> list[Feature]:
    out: list[Feature] = []
    for f in features:
        props = dict(f.get("properties") or {})
        name = props.get("name", "")
        props["region_code"] = f"{prefix}{slugify(name)}"
        out.append({**f, "properties": props})
    return out


def _simplify_coords(coords: list, ratio: float) -> list:
    if simplify_coords_vw is None:
        return coords
    try:
        simplified = simplify_coords_vw(coords, ratio)
        if len(simplified) < 4:
            return coords
        return [list(pt) for pt in simplified]
    except Exception:
        return coords


def _simplify_geometry(geom: dict, ratio: float) -> dict:
    gtype = geom.get("type")
    if gtype == "Polygon":
        rings = [_simplify_coords(r, ratio) for r in geom.get("coordinates", [])]
        return {"type": "Polygon", "coordinates": rings}
    if gtype == "MultiPolygon":
        polys = []
        for poly in geom.get("coordinates", []):
            polys.append([_simplify_coords(r, ratio) for r in poly])
        return {"type": "MultiPolygon", "coordinates": polys}
    return geom


def simplify_features(
    features: Iterable[Feature], ratio: float, min_area_deg2: float
) -> tuple[list[Feature], list[Warning]]:
    out: list[Feature] = []
    warnings: list[Warning] = []
    for f in features:
        new_geom = _simplify_geometry(f.get("geometry") or {}, ratio)
        name = (f.get("properties") or {}).get("name", "")
        try:
            g = shape(new_geom)
            if not g.is_valid:
                g = make_valid(g)
                warnings.append(
                    {
                        "code": "GEOMETRY_FIXED",
                        "message": "Self-intersection auto-repaired",
                        "details": {"name": name},
                    }
                )
            area = float(abs(g.area))
            if area < min_area_deg2:
                warnings.append(
                    {
                        "code": "FEATURE_TOO_SMALL_DROPPED",
                        "message": (
                            f"Feature '{name}' dropped after simplification "
                            f"(area < {min_area_deg2} deg²)"
                        ),
                        "details": {"name": name, "area_deg2": round(area, 6)},
                    }
                )
                continue
            new_geom = mapping(g)
        except Exception:
            pass
        out.append({**f, "geometry": new_geom})
    return out, warnings


def _round_coords(coords: Any, precision: int) -> Any:
    if isinstance(coords, (int, float)):
        return round(float(coords), precision)
    if isinstance(coords, list):
        return [_round_coords(c, precision) for c in coords]
    return coords


def _orient_geometry(geom: dict) -> dict:
    """Orientation conforme à d3-geo / amCharts5.

    En coordonnées GeoJSON (lon, lat), d3-geo attend des anneaux extérieurs
    parcourus dans le sens horaire visuellement (signed area négative dans
    le repère mathématique de Shapely → `sign=-1.0`). Sans cela, le moteur
    interprète l'anneau comme « tout sauf l'intérieur » et recouvre toute
    la mappemonde avec la couleur de remplissage.
    """
    try:
        g = shape(geom)
    except Exception:
        return geom
    if isinstance(g, Polygon):
        return mapping(orient_polygon(g, sign=-1.0))
    if isinstance(g, MultiPolygon):
        return mapping(MultiPolygon([orient_polygon(p, sign=-1.0) for p in g.geoms]))
    return geom


def orient_features(features: Iterable[Feature]) -> list[Feature]:
    out: list[Feature] = []
    for f in features:
        new_geom = _orient_geometry(f.get("geometry") or {})
        out.append({**f, "geometry": new_geom})
    return out


def round_coordinates(
    features: Iterable[Feature], precision: int
) -> list[Feature]:
    out: list[Feature] = []
    for f in features:
        geom = dict(f.get("geometry") or {})
        if "coordinates" in geom:
            geom["coordinates"] = _round_coords(geom["coordinates"], precision)
        out.append({**f, "geometry": geom})
    return out


def sanitize_properties(features: Iterable[Feature]) -> list[Feature]:
    out: list[Feature] = []
    for f in features:
        props = f.get("properties") or {}
        clean = {k: v for k, v in props.items() if k in ALLOWED_PROPS}
        out.append({**f, "type": "Feature", "properties": clean})
    return out


def build_count_warning(
    count: int, expected_min: int, expected_max: int
) -> Warning | None:
    if count < expected_min or count > expected_max:
        return {
            "code": "FEATURE_COUNT_OUT_OF_RANGE",
            "message": f"{count} features (expected {expected_min}-{expected_max})",
            "details": {"count": count},
        }
    return None


def build_unknown_region_warnings(
    features: Iterable[Feature], known_names_normalized: set[str]
) -> list[Warning]:
    warnings: list[Warning] = []
    for f in features:
        name = (f.get("properties") or {}).get("name", "")
        if _norm(name) not in known_names_normalized:
            warnings.append(
                {
                    "code": "REGION_NOT_IN_DATABASE",
                    "message": (
                        f"Region '{name}' has no match in regions table"
                    ),
                    "details": {"name": name},
                }
            )
    return warnings


def run_pipeline(
    file_path: str | Path,
    *,
    aliases: dict[str, str],
    region_code_prefix: str,
    simplify_ratio: float,
    min_feature_area_deg2: float,
    coordinate_precision: int,
    expected_min: int,
    expected_max: int,
    known_region_names_normalized: set[str] | None = None,
) -> PipelineResult:
    raw = list(parse_streaming(file_path))
    deduped, dup_warns = dedupe_by_name(raw)
    normalized = normalize_names(deduped, aliases)
    coded = assign_region_codes(normalized, region_code_prefix)
    simplified, simp_warns = simplify_features(
        coded, simplify_ratio, min_feature_area_deg2
    )
    oriented = orient_features(simplified)
    sanitized = sanitize_properties(oriented)
    rounded = round_coordinates(sanitized, coordinate_precision)
    region_names = [(f.get("properties") or {}).get("name", "") for f in rounded]

    warnings: list[Warning] = []
    warnings.extend(dup_warns)
    warnings.extend(simp_warns)
    count_warn = build_count_warning(len(rounded), expected_min, expected_max)
    if count_warn:
        warnings.append(count_warn)
    if known_region_names_normalized is not None:
        warnings.extend(
            build_unknown_region_warnings(rounded, known_region_names_normalized)
        )

    geojson = {"type": "FeatureCollection", "features": rounded}
    payload = json.dumps(geojson, ensure_ascii=False, separators=(",", ":"))
    return PipelineResult(
        features=rounded,
        region_names=region_names,
        warnings=warnings,
        geojson=geojson,
        processed_size_bytes=len(payload.encode("utf-8")),
    )
