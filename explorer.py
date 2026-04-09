"""Build a static interactive dome explorer site."""
import json
import shutil
from pathlib import Path

import geometry
import insets
import renderer

SITE_DIR = Path(__file__).parent / "site"
RADIUS = renderer.DOME_BASE_RADIUS
CENTER_X = renderer.DOME_CENTER_X
BASE_Y = renderer.DOME_BASE_Y
FIGURE_WIDTH = renderer.WIDTH
FIGURE_HEIGHT = renderer.HEIGHT
MAX_HEIGHT = geometry.dome_profile(0.5, RADIUS)[1]
OUTER_THICKNESS = RADIUS * 0.12
INNER_THICKNESS = RADIUS * 0.16
GAP = RADIUS * 0.10


def _screen_point(local_x: float, local_y: float) -> tuple[float, float]:
    """Convert dome-local coordinates into screen coordinates."""
    return (CENTER_X + local_x, BASE_Y - local_y)


def _region_from_bounds(
    left: float,
    top: float,
    right: float,
    bottom: float,
    padding: float = 0,
) -> dict:
    """Convert rectangle bounds into a hotspot region."""
    return {
        "x": round(left - padding, 1),
        "y": round(top - padding, 1),
        "w": round((right - left) + (padding * 2), 1),
        "h": round((bottom - top) + (padding * 2), 1),
    }


def _path_from_points(points: list[tuple[float, float]], close: bool = False) -> str:
    """Convert points into an SVG path."""
    if not points:
        return ""
    commands = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    commands.extend(f"L {x:.1f} {y:.1f}" for x, y in points[1:])
    if close:
        commands.append("Z")
    return " ".join(commands)


def _profile_points(t_start: float, t_end: float, steps: int = 48) -> list[tuple[float, float]]:
    """Sample points along the pointed-fifth profile."""
    points = []
    for idx in range(steps + 1):
        t = t_start + (t_end - t_start) * (idx / steps)
        local_x, local_y = geometry.dome_profile(t, RADIUS)
        points.append(_screen_point(local_x, local_y))
    return points


def _outer_shell_band(y_top: float, y_bottom: float, steps: int = 48) -> list[tuple[float, float]]:
    """Return a polygon following the outer cutaway shell band."""
    outer_edge = []
    inner_edge = []
    for idx in range(steps + 1):
        y = y_top + (y_bottom - y_top) * (idx / steps)
        _, x_right = geometry.dome_profile_at_height(y, RADIUS)
        screen_y = BASE_Y - y
        outer_edge.append((CENTER_X + x_right, screen_y))
        inner_edge.append((CENTER_X + x_right - OUTER_THICKNESS, screen_y))
    return outer_edge + list(reversed(inner_edge))


def _chain_segments() -> list[dict]:
    """Return SVG line descriptors for the visible chain rings."""
    segments = []
    chain_interval = MAX_HEIGHT / 5
    for idx in range(1, 5):
        y = chain_interval * idx
        _, x_right = geometry.dome_profile_at_height(y, RADIUS)
        screen_y = BASE_Y - y
        segments.append(
            {
                "type": "line",
                "x1": CENTER_X,
                "y1": round(screen_y, 1),
                "x2": round(CENTER_X + x_right, 1),
                "y2": round(screen_y, 1),
                "stroke": "rgba(255, 215, 121, 0.96)",
                "strokeWidth": 5,
                "strokeLinecap": "round",
            }
        )
    return segments


def _chain_regions() -> list[dict]:
    """Return narrow hover regions centered on each chain line."""
    regions = []
    for segment in _chain_segments():
        x1 = float(segment["x1"])
        x2 = float(segment["x2"])
        y = float(segment["y1"])
        regions.append(
            {
                "x": round(x1 - 10, 1),
                "y": round(y - 11, 1),
                "w": round((x2 - x1) + 20, 1),
                "h": 22,
            }
        )
    return regions


def _arch_region() -> dict:
    """Return a hotspot aligned to the upper pointed-fifth profile."""
    profile = _profile_points(0.22, 0.78)
    xs = [x for x, _ in profile]
    ys = [y for _, y in profile]
    _, apex_y = _screen_point(0, MAX_HEIGHT)
    return _region_from_bounds(
        min(xs),
        apex_y - 30,
        max(xs),
        max(ys),
        padding=12,
    )


def _arch_highlight() -> list[dict]:
    """Build highlight geometry for the dome profile."""
    left = _profile_points(0.02, 0.5)
    right = _profile_points(0.5, 0.98)
    apex_x, apex_y = _screen_point(0, MAX_HEIGHT)
    return [
        {
            "type": "path",
            "d": _path_from_points(left),
            "stroke": "rgba(255, 215, 121, 0.96)",
            "strokeWidth": 6,
            "strokeLinecap": "round",
            "fill": "none",
        },
        {
            "type": "path",
            "d": _path_from_points(right),
            "stroke": "rgba(255, 215, 121, 0.96)",
            "strokeWidth": 6,
            "strokeLinecap": "round",
            "fill": "none",
        },
        {
            "type": "ellipse",
            "cx": round(apex_x, 1),
            "cy": round(apex_y + 8, 1),
            "rx": 28,
            "ry": 22,
            "fill": "rgba(255, 213, 128, 0.14)",
            "stroke": "rgba(255, 225, 167, 0.9)",
            "strokeWidth": 3,
        },
    ]


def _herringbone_highlight() -> list[dict]:
    """Build highlight geometry for the visible outer-shell brick band."""
    band = _outer_shell_band(72, 232)
    return [
        {
            "type": "path",
            "d": _path_from_points(band, close=True),
            "fill": "rgba(207, 114, 66, 0.18)",
            "stroke": "rgba(255, 215, 121, 0.94)",
            "strokeWidth": 4,
            "strokeLinejoin": "round",
        },
        {
            "type": "line",
            "x1": 457,
            "y1": 408,
            "x2": 520,
            "y2": 274,
            "stroke": "rgba(255, 230, 176, 0.72)",
            "strokeWidth": 3,
            "strokeLinecap": "round",
        },
        {
            "type": "line",
            "x1": 472,
            "y1": 424,
            "x2": 537,
            "y2": 289,
            "stroke": "rgba(255, 230, 176, 0.58)",
            "strokeWidth": 3,
            "strokeLinecap": "round",
        },
    ]


def _herringbone_region() -> dict:
    """Return a hover region sized to the visible herringbone shell band."""
    band = _outer_shell_band(72, 232)
    xs = [point[0] for point in band]
    ys = [point[1] for point in band]
    return _region_from_bounds(min(xs), min(ys), max(xs), max(ys), padding=8)


def _hoist_region() -> dict:
    """Return a hotspot that wraps the visible hoist machinery."""
    pulley_x = renderer.HOIST_MAST_X + renderer.HOIST_PULLEY_OFFSET_X
    pulley_y = renderer.HOIST_MAST_TOP + renderer.HOIST_PULLEY_OFFSET_Y
    beam_end_y = renderer.HOIST_MAST_BOTTOM - 8
    ox_y = beam_end_y - renderer.HOIST_OX_BASELINE_OFFSET_Y
    return _region_from_bounds(
        min(
            renderer.HOIST_MAST_X - renderer.HOIST_ARM_LEFT,
            pulley_x - (renderer.HOIST_CRATE_WIDTH / 2),
            renderer.HOIST_OX_X - (renderer.HOIST_OX_WIDTH / 2),
        ),
        min(
            renderer.HOIST_MAST_TOP,
            ox_y - renderer.HOIST_OX_TOP_OFFSET,
        ),
        max(
            renderer.HOIST_MAST_X + renderer.HOIST_ARM_RIGHT,
            renderer.HOIST_BEAM_END_X,
            renderer.HOIST_OX_X + (renderer.HOIST_OX_WIDTH / 2),
        ),
        max(
            renderer.HOIST_MAST_BOTTOM,
            pulley_y + renderer.HOIST_CRATE_DROP + renderer.HOIST_CRATE_HEIGHT,
            ox_y - renderer.HOIST_OX_TOP_OFFSET + renderer.HOIST_OX_HEIGHT,
        ),
        padding=12,
    )


def _hoist_highlight() -> list[dict]:
    """Build highlight geometry for the hoist components."""
    mast_x = renderer.HOIST_MAST_X
    mast_top = renderer.HOIST_MAST_TOP
    mast_bottom = renderer.HOIST_MAST_BOTTOM
    pulley_x = mast_x + renderer.HOIST_PULLEY_OFFSET_X
    pulley_y = mast_top + renderer.HOIST_PULLEY_OFFSET_Y
    beam_end_y = mast_bottom - 8
    ox_y = beam_end_y - renderer.HOIST_OX_BASELINE_OFFSET_Y
    return [
        {
            "type": "line",
            "x1": mast_x,
            "y1": mast_top,
            "x2": mast_x,
            "y2": mast_bottom,
            "stroke": "rgba(255, 225, 167, 0.72)",
            "strokeWidth": 8,
            "strokeLinecap": "round",
        },
        {
            "type": "line",
            "x1": mast_x - renderer.HOIST_ARM_LEFT,
            "y1": pulley_y,
            "x2": mast_x + renderer.HOIST_ARM_RIGHT,
            "y2": pulley_y,
            "stroke": "rgba(255, 215, 121, 0.95)",
            "strokeWidth": 4,
            "strokeLinecap": "round",
        },
        {
            "type": "line",
            "x1": mast_x,
            "y1": beam_end_y,
            "x2": renderer.HOIST_BEAM_END_X,
            "y2": beam_end_y,
            "stroke": "rgba(255, 215, 121, 0.95)",
            "strokeWidth": 4,
            "strokeLinecap": "round",
        },
        {
            "type": "line",
            "x1": pulley_x,
            "y1": pulley_y,
            "x2": pulley_x,
            "y2": pulley_y + renderer.HOIST_CRATE_DROP,
            "stroke": "rgba(255, 215, 121, 0.95)",
            "strokeWidth": 4,
            "strokeLinecap": "round",
        },
        {
            "type": "circle",
            "cx": mast_x,
            "cy": mast_bottom - renderer.HOIST_GEAR_OFFSET_Y,
            "r": renderer.HOIST_GEAR_RADIUS + 4,
            "fill": "rgba(255, 213, 128, 0.10)",
            "stroke": "rgba(255, 215, 121, 0.96)",
            "strokeWidth": 4,
        },
        {
            "type": "rect",
            "x": pulley_x - (renderer.HOIST_CRATE_WIDTH / 2),
            "y": pulley_y + renderer.HOIST_CRATE_DROP,
            "w": renderer.HOIST_CRATE_WIDTH,
            "h": renderer.HOIST_CRATE_HEIGHT,
            "rx": 4,
            "fill": "rgba(207, 114, 66, 0.22)",
            "stroke": "rgba(255, 215, 121, 0.9)",
            "strokeWidth": 3,
        },
        {
            "type": "rect",
            "x": renderer.HOIST_OX_X - (renderer.HOIST_OX_WIDTH / 2),
            "y": ox_y - renderer.HOIST_OX_TOP_OFFSET,
            "w": renderer.HOIST_OX_WIDTH,
            "h": renderer.HOIST_OX_HEIGHT,
            "rx": 4,
            "fill": "rgba(212, 197, 169, 0.14)",
            "stroke": "rgba(255, 225, 167, 0.76)",
            "strokeWidth": 3,
        },
    ]

DETAILS = [
    {
        "id": "arch",
        "label": "Pointed arch",
        "hotspot_label": "Pointed-fifth arch profile",
        "title": "Pointed-Fifth Arch",
        "kicker": "Geometry",
        "summary": "The pointed profile sends more load down into the drum and less force sideways.",
        "caption": "A side-by-side comparison of the round arch and Brunelleschi's steeper pointed-fifth profile.",
        "body": [
            "A semicircular dome behaves like a wide arch: it pushes strongly outward at the base and usually needs heavy timber centering while it is being built.",
            "Brunelleschi's pointed-fifth curve is taller and steeper. That geometry redirects more of the masonry load downward, which helped each ring of bricks stabilize itself as construction rose.",
        ],
        "facts": [
            "The arc centers sit at four-fifths of the span from the opposite side.",
            "Less lateral thrust meant less dependence on giant temporary scaffolding.",
        ],
        "regions": [_arch_region()],
        "highlight": _arch_highlight(),
        "image": "assets/pointed-fifth-arch.png",
    },
    {
        "id": "herringbone",
        "label": "Herringbone brickwork",
        "hotspot_label": "Herringbone brickwork on the outer shell",
        "title": "Herringbone Brickwork",
        "kicker": "Masonry technique",
        "summary": "Vertical spine bricks lock the horizontal courses so wet masonry does not slip while the shell climbs.",
        "caption": "Mostly horizontal bricks are interrupted by upright 'spine' bricks that act like teeth in the wall.",
        "body": [
            "The dome was not laid as simple horizontal bands. Brunelleschi inserted vertical bricks at intervals so each fresh course caught against the course below.",
            "That pattern let masons keep building upward without waiting for an enormous full wooden support structure beneath the entire dome.",
        ],
        "facts": [
            "The pattern is visible on the exterior-facing shell.",
            "It helped turn construction from a precarious stack into a controlled climbing system.",
        ],
        "regions": [_herringbone_region()],
        "highlight": _herringbone_highlight(),
        "image": "assets/herringbone-brickwork.png",
    },
    {
        "id": "chains",
        "label": "Chain rings",
        "hotspot_label": "Chain rings embedded in the cutaway shell",
        "title": "Chain Rings",
        "kicker": "Structural restraint",
        "summary": "Stone, iron, and timber chains act like hoops on a barrel, holding the dome against outward thrust.",
        "caption": "The cutaway reveals the continuous tension bands tied into the masonry at intervals.",
        "body": [
            "Brunelleschi embedded horizontal chain rings through the dome to resist the tendency of the walls to spread outward under their own weight.",
            "These bands worked together with the ribs and the double-shell form so the structure behaved like a self-bracing system rather than a dome waiting to collapse until the top closed.",
        ],
        "facts": [
            "The major chain bands sit at multiple levels through the dome.",
            "They combine stone links, iron connectors, and timber elements.",
        ],
        "regions": _chain_regions(),
        "highlight": _chain_segments(),
        "image": "assets/chain-rings.png",
    },
    {
        "id": "hoist",
        "label": "Ox-hoist crane",
        "hotspot_label": "Reversible ox-hoist crane beside the dome",
        "title": "Ox-Hoist Crane",
        "kicker": "Construction logistics",
        "summary": "A reversible hoist let workers raise huge loads without turning the oxen around each time.",
        "caption": "The hoist translates circular animal power into controlled lifting through Brunelleschi's gearing.",
        "body": [
            "Brunelleschi did not just solve geometry. He also designed new machinery to get stone, brick, and timber to the top of the structure.",
            "The reversible gear train meant the oxen could keep walking the same way while the lift direction changed, a major practical advantage on a project of this scale.",
        ],
        "facts": [
            "The crane reduced wasted time at every lift cycle.",
            "Engineering innovation on the site mattered as much as the dome's final shape.",
        ],
        "regions": [_hoist_region()],
        "highlight": _hoist_highlight(),
        "image": "assets/ox-hoist-crane.png",
    },
]


def _write_text(path: Path, content: str):
    """Write a UTF-8 text file, creating parent directories when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_interactive_explorer(output_dir: str = "output/interactive") -> Path:
    """Build the interactive explorer bundle and return its index path."""
    out_dir = Path(output_dir)
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    renderer.render_explorer_figure().write_to_png(str(assets_dir / "brunelleschi-dome-explorer.png"))
    insets.render_arch_comparison().write_to_png(str(assets_dir / "pointed-fifth-arch.png"))
    insets.render_herringbone().write_to_png(str(assets_dir / "herringbone-brickwork.png"))
    insets.render_chain_rings().write_to_png(str(assets_dir / "chain-rings.png"))
    insets.render_ox_hoist().write_to_png(str(assets_dir / "ox-hoist-crane.png"))

    for filename in ["index.html", "styles.css", "app.js"]:
        shutil.copy2(SITE_DIR / filename, out_dir / filename)

    data = {
        "figureImage": "assets/brunelleschi-dome-explorer.png",
        "figureAlt": (
            "Static cutaway view of Brunelleschi's dome with a completed exterior, structural cutaway, "
            "and ox-hoist crane beside it."
        ),
        "figureWidth": FIGURE_WIDTH,
        "figureHeight": FIGURE_HEIGHT,
        "details": DETAILS,
    }
    data_js = f"window.DOME_EXPLORER = {json.dumps(data, indent=2)};\n"
    _write_text(out_dir / "data.js", data_js)

    return out_dir / "index.html"
