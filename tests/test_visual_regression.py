import hashlib
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

import insets
import renderer


def _surface_crop_digest(surface, x: int, y: int, width: int, height: int) -> str:
    arr = np.frombuffer(surface.get_data(), dtype=np.uint8).reshape(
        surface.get_height(), surface.get_stride() // 4, 4
    ).copy()
    crop = arr[y:y + height, x:x + width, :]
    return hashlib.sha256(crop.tobytes()).hexdigest()


def test_explorer_figure_herringbone_band_crop_regression():
    surface = renderer.render_explorer_figure()
    digest = _surface_crop_digest(surface, x=470, y=250, width=120, height=190)
    assert digest == "543e5ef83b7f51561f5a9eab32483e4b5598465081d193765dfae1d2e9f2f227"


def test_herringbone_inset_brick_grid_crop_regression():
    surface = insets.render_herringbone()
    digest = _surface_crop_digest(surface, x=120, y=126, width=280, height=200)
    assert digest == "d63fecb1785e6d0a5b62351bc01fba6720c7df2ec49d88dae404f9a0752c26ad"
