import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path

import explorer


def test_details_have_unique_ids():
    ids = [detail["id"] for detail in explorer.DETAILS]
    assert len(ids) == len(set(ids))


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
