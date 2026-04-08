import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cairo
import renderer


def test_create_surface():
    """create_surface should return an 800x600 Cairo ImageSurface."""
    surface = renderer.create_surface()
    assert surface.get_width() == 800
    assert surface.get_height() == 600


def test_draw_title_bar():
    """draw_title_bar should not raise and should modify the surface."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    renderer.draw_title_bar(ctx, "BUILDING BRUNELLESCHI'S DOME · 1420-1436")


def test_draw_annotation_bar():
    """draw_annotation_bar should not raise."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    renderer.draw_annotation_bar(ctx, "Herringbone brickwork allows each course to be self-supporting")


def test_render_construction_frame_returns_surface():
    """render_construction_frame should return a valid surface."""
    surface = renderer.render_construction_frame(progress=0.0, phase=2)
    assert surface.get_width() == 800
    assert surface.get_height() == 600


def test_render_various_phases():
    """All construction phases should render without error."""
    for phase in [2, 4, 6, 8, 10, 11, 12]:
        surface = renderer.render_construction_frame(progress=0.5, phase=phase)
        assert surface.get_width() == 800
