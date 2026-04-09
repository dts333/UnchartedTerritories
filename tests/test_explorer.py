import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from html.parser import HTMLParser

import explorer
import renderer


def _detail(detail_id: str) -> dict:
    return next(detail for detail in explorer.DETAILS if detail["id"] == detail_id)


def _region_bounds(region: dict) -> tuple[float, float, float, float]:
    return (
        float(region["x"]),
        float(region["y"]),
        float(region["x"]) + float(region["w"]),
        float(region["y"]) + float(region["h"]),
    )


def _region_contains(region: dict, x: float, y: float) -> bool:
    left, top, right, bottom = _region_bounds(region)
    return left <= x <= right and top <= y <= bottom


def test_details_have_unique_ids():
    ids = [detail["id"] for detail in explorer.DETAILS]
    assert len(ids) == len(set(ids))


def test_details_define_regions_and_highlights():
    for detail in explorer.DETAILS:
        assert "regions" in detail
        assert "highlight" in detail
        assert len(detail["regions"]) >= 1
        assert all(region["w"] > 0 for region in detail["regions"])
        assert all(region["h"] > 0 for region in detail["regions"])
        assert len(detail["highlight"]) >= 1


def test_arch_region_tracks_the_upper_dome_profile():
    arch_region = _detail("arch")["regions"][0]
    region_left, _, region_right, _ = _region_bounds(arch_region)
    region_center_x = (region_left + region_right) / 2
    assert abs(region_center_x - renderer.DOME_CENTER_X) < 0.1

    for t in [0.22, 0.3, 0.4, 0.5, 0.6, 0.7, 0.78]:
        point = explorer._screen_point(*explorer.geometry.dome_profile(t, explorer.RADIUS))
        assert _region_contains(arch_region, *point), f"arch region misses dome profile point at t={t}"


def test_herringbone_region_wraps_the_outer_shell_band():
    band_region = _detail("herringbone")["regions"][0]
    for point in explorer._outer_shell_band(72, 232):
        assert _region_contains(band_region, *point), "herringbone region misses the visible shell band"

    assert band_region["x"] > renderer.DOME_CENTER_X


def test_herringbone_highlight_spine_lines_follow_outer_shell_geometry():
    highlight = _detail("herringbone")["highlight"]
    assert highlight[0]["type"] == "path"

    for line in highlight[1:]:
        assert line["type"] == "line"
        assert float(line["x2"]) > float(line["x1"])
        assert abs(float(line["y2"]) - float(line["y1"])) > 100

        for x_key, y_key in [("x1", "y1"), ("x2", "y2")]:
            local_y = renderer.DOME_BASE_Y - float(line[y_key])
            shell_left, shell_right, _ = explorer._outer_shell_strip(local_y)
            x = float(line[x_key])
            assert shell_left <= x <= shell_right


def test_chain_regions_are_centered_on_chain_segments():
    chain_detail = _detail("chains")
    for region, segment in zip(chain_detail["regions"], chain_detail["highlight"], strict=True):
        left, top, right, bottom = _region_bounds(region)
        y = float(segment["y1"])
        x1 = float(segment["x1"])
        x2 = float(segment["x2"])

        assert x1 == renderer.DOME_CENTER_X
        assert abs(((top + bottom) / 2) - y) < 0.1
        assert left <= x1 <= right
        assert left <= x2 <= right


def test_hoist_region_covers_the_visible_hoist_geometry():
    hoist_region = _detail("hoist")["regions"][0]
    pulley_x = renderer.HOIST_MAST_X + renderer.HOIST_PULLEY_OFFSET_X
    pulley_y = renderer.HOIST_MAST_TOP + renderer.HOIST_PULLEY_OFFSET_Y
    beam_end_y = renderer.HOIST_MAST_BOTTOM - 8
    ox_y = beam_end_y - renderer.HOIST_OX_BASELINE_OFFSET_Y

    expected_points = [
        (renderer.HOIST_MAST_X, renderer.HOIST_MAST_TOP),
        (renderer.HOIST_MAST_X, renderer.HOIST_MAST_BOTTOM),
        (pulley_x, pulley_y),
        (pulley_x, pulley_y + renderer.HOIST_CRATE_DROP),
        (renderer.HOIST_MAST_X, renderer.HOIST_MAST_BOTTOM - renderer.HOIST_GEAR_OFFSET_Y),
        (renderer.HOIST_BEAM_END_X, beam_end_y),
        (renderer.HOIST_OX_X, ox_y),
    ]

    for point in expected_points:
        assert _region_contains(hoist_region, *point), f"hoist region misses anchor point {point}"


def test_detail_specs_drive_payload_and_assets():
    details = explorer.build_details()

    assert [detail["id"] for detail in details] == [spec.id for spec in explorer.DETAIL_SPECS]
    assert [detail["image"] for detail in details] == [
        f"assets/{spec.image_name}" for spec in explorer.DETAIL_SPECS
    ]
    assert [spec.render_fn.__name__ for spec in explorer.DETAIL_SPECS] == [
        "render_arch_comparison",
        "render_herringbone",
        "render_chain_rings",
        "render_ox_hoist",
    ]


def test_highlight_shapes_use_svg_attribute_names():
    for detail in explorer.build_details():
        for shape in detail["highlight"]:
            if shape["type"] == "rect":
                assert "w" not in shape
                assert "h" not in shape
                assert "width" in shape
                assert "height" in shape


def test_build_interactive_explorer_writes_bundle(tmp_path):
    index_path = explorer.build_interactive_explorer(tmp_path / "interactive")

    assert index_path.name == "index.html"
    assert index_path.exists()

    expected = [
        index_path,
        index_path.parent / "styles.css",
        index_path.parent / "app.js",
        index_path.parent / "data.js",
        index_path.parent / "assets" / "brunelleschi-dome-explorer.png",
        index_path.parent / "assets" / "pointed-fifth-arch.png",
        index_path.parent / "assets" / "herringbone-brickwork.png",
        index_path.parent / "assets" / "chain-rings.png",
        index_path.parent / "assets" / "ox-hoist-crane.png",
    ]

    for path in expected:
        assert Path(path).exists(), f"Expected build artifact {path} to exist"

    data_js = (index_path.parent / "data.js").read_text(encoding="utf-8")
    assert "window.DOME_EXPLORER" in data_js
    assert "Pointed-Fifth Arch" in data_js

    payload = json.loads(
        data_js.removeprefix("window.DOME_EXPLORER = ").removesuffix(";\n")
    )
    assert payload["figureWidth"] == renderer.WIDTH
    assert payload["figureHeight"] == renderer.HEIGHT
    assert [detail["id"] for detail in payload["details"]] == [detail["id"] for detail in explorer.build_details()]


class _IndexParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.script_srcs = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if "id" in attrs_dict:
            self.ids.add(attrs_dict["id"])
        if tag == "script" and "src" in attrs_dict:
            self.script_srcs.append(attrs_dict["src"])


def test_index_html_contains_expected_app_mounts(tmp_path):
    index_path = explorer.build_interactive_explorer(tmp_path / "interactive")
    parser = _IndexParser()
    parser.feed(index_path.read_text(encoding="utf-8"))

    assert {"dome-figure", "highlight-layer", "hotspots", "topic-list", "detail-image"} <= parser.ids
    assert parser.script_srcs[-2:] == ["data.js", "app.js"]
