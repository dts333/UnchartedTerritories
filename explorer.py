"""Build a static interactive dome explorer site."""
import json
import shutil
from pathlib import Path

import insets
import renderer

SITE_DIR = Path(__file__).parent / "site"

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
        "hotspot": {"x": 398, "y": 182},
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
        "hotspot": {"x": 258, "y": 310},
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
        "hotspot": {"x": 532, "y": 335},
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
        "hotspot": {"x": 676, "y": 380},
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
        "details": DETAILS,
    }
    data_js = f"window.DOME_EXPLORER = {json.dumps(data, indent=2)};\n"
    _write_text(out_dir / "data.js", data_js)

    return out_dir / "index.html"
