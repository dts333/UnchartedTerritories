import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import palette


def test_colors_are_rgb_tuples():
    """All palette colors should be (r, g, b) tuples with values 0.0-1.0."""
    colors = [
        palette.BG, palette.TERRACOTTA, palette.SIENNA, palette.DARK_BROWN,
        palette.GOLD, palette.CREAM, palette.TEXT, palette.DRUM_STONE,
    ]
    for color in colors:
        assert isinstance(color, tuple), f"{color} is not a tuple"
        assert len(color) == 3, f"{color} doesn't have 3 components"
        assert all(0.0 <= c <= 1.0 for c in color), f"{color} has out-of-range values"


def test_set_source_rgb_helper():
    """set_color should call ctx.set_source_rgb with the color tuple."""
    class FakeCtx:
        def __init__(self):
            self.calls = []
        def set_source_rgb(self, r, g, b):
            self.calls.append((r, g, b))

    ctx = FakeCtx()
    palette.set_color(ctx, palette.GOLD)
    assert len(ctx.calls) == 1
    assert ctx.calls[0] == palette.GOLD
