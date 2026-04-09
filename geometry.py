"""Parametric geometry for Brunelleschi's dome.

The dome uses a pointed-fifth arch profile: two circular arcs whose centers
are each placed at 4/5 of the base diameter from the opposite side.

For a dome with base radius R (diameter D = 2R):
- Right arc center: at x = -R + (4/5)*D = -R + 8R/5 = 3R/5 from origin
- Left arc center: at x = R - (4/5)*D = R - 8R/5 = -3R/5 from origin
- Arc radius: distance from each center to the OPPOSITE base corner
  = distance from (3R/5, 0) to (-R, 0) = 3R/5 + R = 8R/5

The left half of the dome is drawn by the arc centered on the RIGHT side,
and vice versa.
"""
import math


def dome_profile(t: float, base_radius: float) -> tuple[float, float]:
    """Return (x, y) on the dome profile for parameter t in [0, 1].

    t=0: left base (-base_radius, 0)
    t=0.5: apex (~0, max_height)
    t=1: right base (base_radius, 0)
    """
    R = base_radius
    arc_r = 8 * R / 5  # 1.6 * R

    # Right arc center at (3R/5, 0) draws the LEFT side of the dome
    cx_right = 3 * R / 5
    # Left arc center at (-3R/5, 0) draws the RIGHT side of the dome
    cx_left = -3 * R / 5

    if t <= 0.5:
        # Left half: arc centered at (cx_right, 0)
        # At t=0: point is (-R, 0). Angle from center: atan2(0, -R - cx_right) = atan2(0, -8R/5) = pi
        # At t=0.5: apex at (0, y). Angle: atan2(y, 0 - cx_right) = atan2(y, -3R/5)
        # We need to find the apex angle. At apex, x=0:
        # 0 = cx_right + arc_r * cos(angle) => cos(angle) = -cx_right/arc_r = -(3R/5)/(8R/5) = -3/8
        angle_base = math.pi
        angle_apex = math.acos(-3.0 / 8.0)  # about 112 degrees

        # Interpolate angle from base to apex
        angle = angle_base + (angle_apex - angle_base) * (t / 0.5)
        x = cx_right + arc_r * math.cos(angle)
        y = arc_r * math.sin(angle)
    else:
        # Right half: arc centered at (cx_left, 0)
        # At t=0.5: apex. cos(angle) = -cx_left/arc_r = (3R/5)/(8R/5) = 3/8
        # At t=1: point is (R, 0). Angle from center: atan2(0, R - cx_left) = atan2(0, 8R/5) = 0
        angle_apex = math.pi - math.acos(-3.0 / 8.0)  # symmetric with left side
        # Wait, let me think about this differently. For the right half:
        # cx_left = -3R/5. The apex is at x=0.
        # cos(angle_apex) = (0 - cx_left) / arc_r = (3R/5) / (8R/5) = 3/8
        # sin(angle_apex) > 0, so angle_apex = acos(3/8)
        angle_apex = math.acos(3.0 / 8.0)
        angle_base = 0.0  # at (R, 0)

        frac = (t - 0.5) / 0.5
        angle = angle_apex + (angle_base - angle_apex) * frac
        x = cx_left + arc_r * math.cos(angle)
        y = arc_r * math.sin(angle)

    return (x, y)


def dome_profile_at_height(y: float, base_radius: float) -> tuple[float, float]:
    """Return (x_left, x_right) where the dome profile crosses height y.

    Uses the pointed-fifth geometry. For a given height, find the x coordinates
    on the left arc (centered at cx_right) and right arc (centered at cx_left).
    Heights below the springing ring clamp to the base width, and heights at or
    above the apex clamp to the centerline.
    """
    R = base_radius
    arc_r = 8 * R / 5
    cx_right = 3 * R / 5
    cx_left = -3 * R / 5
    apex_y = dome_profile(0.5, base_radius)[1]

    if y <= 0:
        return (-R, R)

    if y >= apex_y:
        return (0.0, 0.0)

    sin_a = y / arc_r
    cos_a = math.sqrt(1 - sin_a ** 2)

    # Left side: arc centered at cx_right, we want the x < 0 intersection
    x_left = cx_right - cos_a * arc_r

    # Right side: arc centered at cx_left, we want the x > 0 intersection
    x_right = cx_left + cos_a * arc_r

    return (x_left, x_right)


def octagon_points(radius: float) -> list[tuple[float, float]]:
    """Return 8 vertices of a regular octagon inscribed in a circle.

    First vertex at top (12 o'clock), proceeding clockwise.
    """
    points = []
    for i in range(8):
        angle = math.pi / 2 - i * (2 * math.pi / 8)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    return points
