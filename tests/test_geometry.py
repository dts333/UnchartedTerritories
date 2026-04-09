import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import geometry


def test_dome_profile_endpoints():
    """Profile at t=0 and t=1 should be at the base corners."""
    base_radius = 100
    x0, y0 = geometry.dome_profile(0.0, base_radius)
    x1, y1 = geometry.dome_profile(1.0, base_radius)
    assert abs(x0 - (-base_radius)) < 1.0, f"Left endpoint x={x0}, expected {-base_radius}"
    assert abs(y0) < 1.0, f"Left endpoint y={y0}, expected 0"
    assert abs(x1 - base_radius) < 1.0, f"Right endpoint x={x1}, expected {base_radius}"
    assert abs(y1) < 1.0, f"Right endpoint y={y1}, expected 0"


def test_dome_profile_apex_is_centered():
    """Profile at t=0.5 should be at x~0 and y > 0 (above base)."""
    x, y = geometry.dome_profile(0.5, 100)
    assert abs(x) < 1.0, f"Apex x={x}, expected ~0"
    assert y > 80, f"Apex y={y}, expected > 80 (dome is tall)"


def test_dome_profile_is_symmetric():
    """Profile should be symmetric about x=0."""
    for t in [0.1, 0.2, 0.3, 0.4]:
        x_left, y_left = geometry.dome_profile(t, 100)
        x_right, y_right = geometry.dome_profile(1.0 - t, 100)
        assert abs(x_left + x_right) < 1.0, f"Not symmetric at t={t}: {x_left} vs {x_right}"
        assert abs(y_left - y_right) < 1.0, f"Heights differ at t={t}: {y_left} vs {y_right}"


def test_dome_profile_is_pointed():
    """Pointed-fifth arch should be taller than a semicircle (height > radius)."""
    _, apex_y = geometry.dome_profile(0.5, 100)
    assert apex_y > 100, f"Apex height {apex_y} is not greater than radius 100"


def test_dome_profile_at_height():
    """dome_profile_at_height should return left and right x for a given y."""
    x_left, x_right = geometry.dome_profile_at_height(0, 100)
    assert abs(x_left - (-100)) < 1.0
    assert abs(x_right - 100) < 1.0
    # At some mid-height, dome should be narrower than base
    x_left_mid, x_right_mid = geometry.dome_profile_at_height(80, 100)
    assert x_right_mid < 100, "Dome should narrow above base"
    assert x_left_mid > -100, "Dome should narrow above base"


def test_dome_profile_at_height_clamps_outside_visible_profile():
    """Heights outside the dome profile should clamp to valid intersections."""
    radius = 100
    _, apex_y = geometry.dome_profile(0.5, radius)

    assert geometry.dome_profile_at_height(-10, radius) == (-radius, radius)
    assert geometry.dome_profile_at_height(apex_y, radius) == (0.0, 0.0)
    assert geometry.dome_profile_at_height(apex_y + 10, radius) == (0.0, 0.0)


def test_octagon_points():
    """Should return 8 points on a circle of given radius."""
    points = geometry.octagon_points(100)
    assert len(points) == 8
    for x, y in points:
        dist = math.sqrt(x**2 + y**2)
        assert abs(dist - 100) < 0.1, f"Point ({x},{y}) not on circle: dist={dist}"
