import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cairo
import geometry
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


def test_render_explorer_figure_returns_surface():
    """The interactive explorer figure should render without error."""
    surface = renderer.render_explorer_figure()
    assert surface.get_width() == 800
    assert surface.get_height() == 600


def test_drum_base_elements_align_with_dome_footprint():
    """Stone trim at the dome base should not overhang past the dome footprint."""
    assert renderer.DRUM_WIDTH == renderer.DOME_RIGHT_X - renderer.DOME_LEFT_X
    assert renderer.DOME_LEFT_X == renderer.DOME_CENTER_X - renderer.DOME_BASE_RADIUS
    assert renderer.DOME_RIGHT_X == renderer.DOME_CENTER_X + renderer.DOME_BASE_RADIUS


def test_lantern_stack_is_centered_on_the_dome_axis():
    """The lantern should read as a centered shaft, cap, sphere, and cross."""
    _, apex_y = geometry.dome_profile(0.5, renderer.DOME_BASE_RADIUS)
    _, dome_right_near_apex = geometry.dome_profile_at_height(apex_y - 12, renderer.DOME_BASE_RADIUS)

    assert renderer.LANTERN_SHAFT_TOP_HALF_WIDTH <= renderer.LANTERN_SHAFT_HALF_WIDTH
    assert renderer.LANTERN_SHAFT_HALF_WIDTH <= dome_right_near_apex
    assert renderer.LANTERN_CAP_HALF_WIDTH >= renderer.LANTERN_SHAFT_TOP_HALF_WIDTH
    assert renderer.LANTERN_SPHERE_RADIUS > 0
    assert renderer.LANTERN_CROSS_HEIGHT > 0


def test_render_explorer_figure_uses_flat_drum_profile(monkeypatch):
    """The static explorer should omit the raised drum sidewalls."""
    captured = []
    original = renderer.draw_drum

    def wrapped(ctx, progress, show_sidewalls=True):
        captured.append(show_sidewalls)
        return original(ctx, progress, show_sidewalls=show_sidewalls)

    monkeypatch.setattr(renderer, "draw_drum", wrapped)
    renderer.render_explorer_figure()

    assert captured == [False]
