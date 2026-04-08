"""Cairo renderer for Brunelleschi's dome construction frames.

Draws the main construction view: background, title bar, dome (exterior left,
cutaway right), and annotation bar.
"""
import math
import cairo

import geometry
import palette

WIDTH = 800
HEIGHT = 600
DOME_BASE_RADIUS = 210
DOME_CENTER_X = WIDTH // 2
DOME_BASE_Y = 468
DOME_LEFT_X = DOME_CENTER_X - DOME_BASE_RADIUS
DOME_RIGHT_X = DOME_CENTER_X + DOME_BASE_RADIUS
DRUM_WIDTH = 420
PODIUM_WIDTH = 468
DRUM_CORNICE_HEIGHT = 16
LANTERN_SHAFT_HALF_WIDTH = 24
LANTERN_SHAFT_TOP_HALF_WIDTH = 20
LANTERN_SHAFT_HEIGHT = 52
LANTERN_CAP_HALF_WIDTH = 28
LANTERN_CAP_HEIGHT = 22
LANTERN_SPHERE_RADIUS = 5
LANTERN_CROSS_HEIGHT = 12
LANTERN_CROSS_ARM = 4
HOIST_MAST_X = 660
HOIST_MAST_TOP = 138
HOIST_MAST_BOTTOM = 438
HOIST_PULLEY_OFFSET_X = 26
HOIST_PULLEY_OFFSET_Y = 18
HOIST_ARM_LEFT = 58
HOIST_ARM_RIGHT = 34
HOIST_CRATE_DROP = 116
HOIST_CRATE_WIDTH = 32
HOIST_CRATE_HEIGHT = 26
HOIST_GEAR_OFFSET_Y = 42
HOIST_GEAR_RADIUS = 24
HOIST_BEAM_END_X = 724
HOIST_OX_X = 742
HOIST_OX_BASELINE_OFFSET_Y = 6
HOIST_OX_TOP_OFFSET = 14
HOIST_OX_WIDTH = 44
HOIST_OX_HEIGHT = 24

# Phase annotations
PHASE_ANNOTATIONS = {
    2: "The octagonal drum rises above the cathedral, creating the stable base for the dome.",
    4: "Two concentric shells start together. The hollow gap cuts weight while keeping strength.",
    6: "Herringbone brickwork locks fresh masonry in place, letting each course support the next.",
    8: "Major ribs and chain rings organize the dome and resist the outward thrust of the masonry.",
    10: "Each narrowing ring closes into a stable circuit, so the dome can keep climbing without full centering.",
    11: "The lantern crowns the oculus and compresses the masonry ring at the very top.",
    12: "Completed in 1436: a double-shell masonry dome built without the vast timber centering everyone expected.",
}


def create_surface() -> cairo.ImageSurface:
    """Create a new 800x600 ARGB surface."""
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)


def _rounded_rect(ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float):
    """Create a rounded rectangle path."""
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -1.5708, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 1.5708)
    ctx.arc(x + r, y + h - r, r, 1.5708, 3.14159)
    ctx.arc(x + r, y + r, r, 3.14159, 4.71239)
    ctx.close_path()


def _wrap_text(ctx: cairo.Context, text: str, max_width: float) -> list[str]:
    """Wrap text to fit inside a fixed width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and ctx.text_extents(candidate).width > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_wrapped_text(
    ctx: cairo.Context,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float,
    max_lines: int | None = None,
):
    """Draw wrapped text with optional line limiting."""
    lines = _wrap_text(ctx, text, max_width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            last = lines[-1].rstrip(".")
            while ctx.text_extents(f"{last}...").width > max_width and last:
                last = last[:-1]
            lines[-1] = f"{last}..."

    for idx, line in enumerate(lines):
        ctx.move_to(x, y + idx * line_height)
        ctx.show_text(line)


def draw_background(ctx: cairo.Context):
    """Fill the canvas with a painted dusk backdrop and Florence silhouette."""
    sky = cairo.LinearGradient(0, 0, 0, HEIGHT)
    sky.add_color_stop_rgb(0.0, *palette.SKY_TOP)
    sky.add_color_stop_rgb(0.55, *palette.BG)
    sky.add_color_stop_rgb(1.0, *palette.SKY_BOTTOM)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source(sky)
    ctx.fill()

    glow = cairo.RadialGradient(WIDTH * 0.32, HEIGHT * 0.28, 10, WIDTH * 0.32, HEIGHT * 0.28, 240)
    glow.add_color_stop_rgba(0.0, *palette.GLOW, 0.35)
    glow.add_color_stop_rgba(1.0, *palette.GLOW, 0.0)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source(glow)
    ctx.fill()

    palette.set_color_alpha(ctx, palette.PANEL, 0.55)
    ctx.rectangle(0, HEIGHT - 170, WIDTH, 170)
    ctx.fill()

    skyline = [
        (24, 368, 82, 54),
        (86, 345, 42, 78),
        (130, 360, 90, 64),
        (220, 338, 54, 92),
        (286, 352, 72, 70),
        (360, 330, 38, 98),
        (458, 350, 74, 76),
        (534, 332, 48, 94),
        (596, 360, 90, 64),
        (688, 346, 56, 80),
    ]
    palette.set_color_alpha(ctx, palette.VOID, 0.85)
    for x, y, w, h in skyline:
        ctx.rectangle(x, y, w, h)
        ctx.fill()

    palette.set_color_alpha(ctx, palette.GOLD, 0.12)
    ctx.rectangle(0, HEIGHT - 150, WIDTH, 2)
    ctx.fill()


def draw_title_bar(ctx: cairo.Context, title: str):
    """Draw the top title bar with refined framing and subtitle."""
    panel_x = 34
    panel_y = 22
    panel_w = WIDTH - 68
    panel_h = 58

    _rounded_rect(ctx, panel_x, panel_y, panel_w, panel_h, 16)
    palette.set_color_alpha(ctx, palette.PANEL, 0.9)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.55)
    ctx.set_line_width(1.2)
    ctx.stroke()

    ctx.select_font_face("serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(24)
    palette.set_color(ctx, palette.TEXT)
    extents = ctx.text_extents(title)
    ctx.move_to((WIDTH - extents.width) / 2, panel_y + 26)
    ctx.show_text(title)

    subtitle = "Innovation in brick, structure, and lifting technology"
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11)
    palette.set_color(ctx, palette.TEXT_MUTED)
    subtitle_extents = ctx.text_extents(subtitle)
    ctx.move_to((WIDTH - subtitle_extents.width) / 2, panel_y + 45)
    ctx.show_text(subtitle)


def draw_annotation_bar(ctx: cairo.Context, text: str):
    """Draw the bottom annotation bar with explanation text."""
    box_x = 86
    box_y = HEIGHT - 94
    box_w = WIDTH - 172
    box_h = 68

    _rounded_rect(ctx, box_x, box_y, box_w, box_h, 18)
    palette.set_color_alpha(ctx, palette.ANNOTATION_BG, 0.95)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.8)
    ctx.set_line_width(1.4)
    ctx.stroke()

    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    ctx.move_to(box_x + 18, box_y + 19)
    ctx.show_text("WHY IT MATTERS")

    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(13)
    palette.set_color(ctx, palette.TEXT)
    _draw_wrapped_text(ctx, text, box_x + 18, box_y + 40, box_w - 36, 18, max_lines=2)


def draw_split_labels(ctx: cairo.Context):
    """Draw side badges for the exterior and cutaway views."""
    for x, text in [(54, "EXTERIOR VIEW"), (WIDTH - 214, "CUTAWAY VIEW")]:
        _rounded_rect(ctx, x, 95, 160, 28, 14)
        palette.set_color_alpha(ctx, palette.PANEL_ALT, 0.82)
        ctx.fill_preserve()
        palette.set_color_alpha(ctx, palette.GOLD, 0.7)
        ctx.set_line_width(1)
        ctx.stroke()

        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        palette.set_color(ctx, palette.GOLD)
        extents = ctx.text_extents(text)
        ctx.move_to(x + (160 - extents.width) / 2, 113)
        ctx.show_text(text)

    palette.set_color_alpha(ctx, palette.GOLD, 0.32)
    ctx.set_dash([7, 6])
    ctx.set_line_width(1.2)
    ctx.move_to(WIDTH // 2, 124)
    ctx.line_to(WIDTH // 2, HEIGHT - 112)
    ctx.stroke()
    ctx.set_dash([])


def draw_drum(ctx: cairo.Context, progress: float, show_sidewalls: bool = True):
    """Draw the octagonal drum and cathedral body beneath it."""
    visible_height = 72 * progress

    podium_x = DOME_CENTER_X - PODIUM_WIDTH / 2
    podium_y = DOME_BASE_Y + 10
    podium_w = PODIUM_WIDTH
    podium_h = 78
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(podium_x, podium_y, podium_w, podium_h)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(2)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.15)
    for x in range(int(podium_x + 16), int(podium_x + podium_w), 36):
        ctx.rectangle(x, podium_y + 4, 2, podium_h - 8)
        ctx.fill()

    drum_x = DOME_LEFT_X
    plinth_top = DOME_BASE_Y - 6
    plinth_h = DRUM_CORNICE_HEIGHT
    palette.set_color(ctx, palette.STONE_LIGHT)
    ctx.rectangle(drum_x, plinth_top, DRUM_WIDTH, plinth_h)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.6)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.14)
    for x in range(int(drum_x + 10), int(drum_x + DRUM_WIDTH), 34):
        ctx.rectangle(x, plinth_top + 3, 2, plinth_h - 6)
        ctx.fill()

    if visible_height <= 0 or not show_sidewalls:
        return

    drum_top = DOME_BASE_Y - visible_height
    drum_w = DRUM_WIDTH
    drum_x = DOME_LEFT_X

    palette.set_color(ctx, palette.STONE_LIGHT)
    ctx.rectangle(drum_x, drum_top, drum_w, visible_height)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(2)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.20)
    for offset in range(10, int(visible_height), 14):
        ctx.rectangle(drum_x + 2, drum_top + offset, drum_w - 4, 1.5)
        ctx.fill()

    if visible_height >= 18:
        window_y = max(drum_top + 14, DOME_BASE_Y - 42)
        window_w = 30
        window_h = min(34, visible_height - 16)
        palette.set_color_alpha(ctx, palette.VOID, 0.72)
        for center_x in [DOME_CENTER_X - 126, DOME_CENTER_X - 42, DOME_CENTER_X + 42, DOME_CENTER_X + 126]:
            ctx.rectangle(center_x - window_w / 2, window_y, window_w, max(window_h, 4))
            ctx.fill()
            palette.set_color_alpha(ctx, palette.GOLD, 0.22)
            ctx.set_line_width(1)
            ctx.rectangle(center_x - window_w / 2, window_y, window_w, max(window_h, 4))
            ctx.stroke()


def _get_dome_max_height() -> float:
    """Get the apex height of the dome."""
    _, apex_y = geometry.dome_profile(0.5, DOME_BASE_RADIUS)
    return apex_y


def _profile_points_until_height(current_height: float, t_start: float, t_end: float, steps: int = 160) -> list[tuple[float, float]]:
    """Return profile points from a side of the dome up to a height cutoff."""
    points = []
    last_point = None
    for idx in range(steps + 1):
        t = t_start + (t_end - t_start) * (idx / steps)
        x, y = geometry.dome_profile(t, DOME_BASE_RADIUS)
        if y > current_height:
            if last_point and y != last_point[1]:
                frac = (current_height - last_point[1]) / (y - last_point[1])
                cut_x = last_point[0] + frac * (x - last_point[0])
                points.append((cut_x, current_height))
            break
        points.append((x, y))
        last_point = (x, y)
    return points


def _stroke_path(ctx: cairo.Context, points: list[tuple[float, float]]):
    """Stroke a list of screen points."""
    if len(points) < 2:
        return
    ctx.move_to(*points[0])
    for point in points[1:]:
        ctx.line_to(*point)
    ctx.stroke()


def draw_dome_exterior(ctx: cairo.Context, height_frac: float):
    """Draw the exterior (left half) of the dome up to height_frac."""
    if height_frac <= 0:
        return

    max_height = _get_dome_max_height()
    current_height = max_height * height_frac
    points = _profile_points_until_height(current_height, 0.0, 0.5)
    if len(points) < 2:
        return

    screen_points = [(DOME_CENTER_X + px, DOME_BASE_Y - py) for px, py in points]
    top_y = DOME_BASE_Y - current_height
    screen_points.extend([(DOME_CENTER_X, top_y), (DOME_CENTER_X, DOME_BASE_Y)])

    ctx.save()
    ctx.rectangle(0, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    ctx.move_to(*screen_points[0])
    for point in screen_points[1:]:
        ctx.line_to(*point)
    ctx.close_path()

    fill = cairo.LinearGradient(DOME_CENTER_X - 150, DOME_BASE_Y, DOME_CENTER_X - 10, DOME_BASE_Y - max_height)
    fill.add_color_stop_rgb(0.0, *palette.BRICK_SHADOW)
    fill.add_color_stop_rgb(0.35, *palette.SIENNA)
    fill.add_color_stop_rgb(0.75, *palette.TERRACOTTA)
    fill.add_color_stop_rgb(1.0, *palette.BRICK_LIGHT)
    ctx.set_source(fill)
    ctx.fill_preserve()

    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(2.2)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.BRICK_LIGHT, 0.18)
    ctx.move_to(DOME_CENTER_X - 152, DOME_BASE_Y - 12)
    ctx.curve_to(DOME_CENTER_X - 126, DOME_BASE_Y - 165, DOME_CENTER_X - 74, DOME_BASE_Y - 252, DOME_CENTER_X - 26, top_y + 16)
    ctx.set_line_width(14)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.RIB_DARK, 0.32)
    ctx.set_line_width(1)
    course_spacing = 8
    for cy in range(10, int(current_height), course_spacing):
        x_left, _ = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        screen_y = DOME_BASE_Y - cy
        ctx.move_to(DOME_CENTER_X + x_left, screen_y)
        ctx.line_to(DOME_CENTER_X, screen_y)
        ctx.stroke()

    palette.set_color_alpha(ctx, palette.RIB_DARK, 0.72)
    ctx.set_line_width(3)
    for rib_frac in [0.18, 0.38, 0.62, 0.84]:
        rib_points = []
        for cy in range(0, int(current_height), 5):
            x_left, _ = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            rib_x = DOME_CENTER_X + x_left * (1 - rib_frac)
            rib_points.append((rib_x, DOME_BASE_Y - cy))
        _stroke_path(ctx, rib_points)

    ctx.restore()


def draw_dome_cutaway(
    ctx: cairo.Context,
    height_frac: float,
    show_ribs: bool = False,
    show_chains: bool = False,
    show_herringbone: bool = False,
):
    """Draw the cutaway (right half) showing inner/outer shells, ribs, chains."""
    if height_frac <= 0:
        return

    max_height = _get_dome_max_height()
    current_height = max_height * height_frac

    outer_thickness = DOME_BASE_RADIUS * 0.12
    inner_thickness = DOME_BASE_RADIUS * 0.16
    gap = DOME_BASE_RADIUS * 0.10

    ctx.save()
    ctx.rectangle(WIDTH // 2, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    for cy in range(0, int(current_height), 2):
        _, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy

        outer_left = DOME_CENTER_X + x_right - outer_thickness
        outer_right = DOME_CENTER_X + x_right
        inner_right = outer_left - gap
        inner_left = inner_right - inner_thickness

        palette.set_color_alpha(ctx, palette.VOID, 0.45)
        ctx.rectangle(max(DOME_CENTER_X, inner_right), screen_y, max(outer_left - inner_right, 0), 2)
        ctx.fill()

        palette.set_color(ctx, palette.SIENNA)
        ctx.rectangle(max(DOME_CENTER_X, outer_left), screen_y, max(outer_right - max(DOME_CENTER_X, outer_left), 0), 2)
        ctx.fill()

        palette.set_color(ctx, palette.TERRACOTTA)
        ctx.rectangle(max(DOME_CENTER_X, inner_left), screen_y, max(inner_right - max(DOME_CENTER_X, inner_left), 0), 2)
        ctx.fill()

    outer_right_pts = []
    outer_left_pts = []
    inner_right_pts = []
    inner_left_pts = []
    for cy in range(0, int(current_height), 4):
        _, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy
        outer_right = DOME_CENTER_X + x_right
        outer_left = outer_right - outer_thickness
        inner_right = outer_left - gap
        inner_left = inner_right - inner_thickness
        outer_right_pts.append((outer_right, screen_y))
        outer_left_pts.append((outer_left, screen_y))
        inner_right_pts.append((inner_right, screen_y))
        inner_left_pts.append((inner_left, screen_y))

    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1.6)
    for points in [outer_right_pts, outer_left_pts, inner_right_pts, inner_left_pts]:
        _stroke_path(ctx, points)

    if show_herringbone:
        palette.set_color_alpha(ctx, palette.BRICK_SHADOW, 0.8)
        brick_h = 9
        brick_w = 10
        for cy in range(8, int(current_height), brick_h):
            _, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            if x_right <= 0:
                continue
            screen_y = DOME_BASE_Y - cy
            shell_left = int(DOME_CENTER_X + x_right - outer_thickness)
            shell_right = int(DOME_CENTER_X + x_right)
            row = cy // brick_h
            for col_idx, bx in enumerate(range(max(shell_left, DOME_CENTER_X), shell_right, brick_w)):
                if (row + col_idx) % 4 == 0:
                    ctx.rectangle(bx + brick_w // 3, screen_y - brick_h, max(brick_w // 3, 2), brick_h)
                    ctx.fill()

    if show_chains:
        chain_interval = max_height / 5
        palette.set_color_alpha(ctx, palette.GOLD, 0.92)
        ctx.set_line_width(3.2)
        for idx in range(1, 5):
            cy = chain_interval * idx
            if cy > current_height:
                break
            _, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            screen_y = DOME_BASE_Y - cy
            ctx.move_to(DOME_CENTER_X, screen_y)
            ctx.line_to(DOME_CENTER_X + x_right, screen_y)
            ctx.stroke()

    if show_ribs:
        palette.set_color_alpha(ctx, palette.RIB_DARK, 0.88)
        ctx.set_line_width(3.6)
        for rib_frac in [0.24, 0.5, 0.78]:
            rib_points = []
            for cy in range(0, int(current_height), 5):
                _, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
                rib_x = DOME_CENTER_X + x_right * rib_frac
                rib_points.append((rib_x, DOME_BASE_Y - cy))
            _stroke_path(ctx, rib_points)

    if current_height > max_height * 0.28:
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        palette.set_color(ctx, palette.GOLD)

        callout_y = DOME_BASE_Y - min(current_height * 0.58, max_height * 0.58)
        ctx.move_to(DOME_CENTER_X + 130, callout_y)
        ctx.show_text("double shell")
        ctx.set_line_width(1.2)
        ctx.move_to(DOME_CENTER_X + 118, callout_y - 4)
        ctx.line_to(DOME_CENTER_X + 78, callout_y - 16)
        ctx.stroke()

        if show_chains and current_height > max_height * 0.45:
            chain_y = DOME_BASE_Y - max_height * 0.4
            ctx.move_to(DOME_CENTER_X + 120, chain_y - 6)
            ctx.show_text("chain rings")
            ctx.move_to(DOME_CENTER_X + 108, chain_y - 8)
            ctx.line_to(DOME_CENTER_X + 70, chain_y - 8)
            ctx.stroke()

    ctx.restore()


def draw_lantern(ctx: cairo.Context, progress: float = 1.0):
    """Draw the lantern atop the completed dome."""
    max_height = _get_dome_max_height()
    lantern_base_y = DOME_BASE_Y - max_height
    if progress <= 0:
        return

    shaft_height = LANTERN_SHAFT_HEIGHT * progress
    shaft_top = lantern_base_y - shaft_height

    # A flat stone platform keeps the lantern reading as a centered vertical stack.
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(
        DOME_CENTER_X - LANTERN_SHAFT_HALF_WIDTH,
        lantern_base_y - 4,
        LANTERN_SHAFT_HALF_WIDTH * 2,
        8,
    )
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.4)
    ctx.stroke()

    body_points = [
        (DOME_CENTER_X - LANTERN_SHAFT_HALF_WIDTH, lantern_base_y),
        (DOME_CENTER_X - LANTERN_SHAFT_HALF_WIDTH, shaft_top + 8),
        (DOME_CENTER_X - LANTERN_SHAFT_TOP_HALF_WIDTH, shaft_top),
        (DOME_CENTER_X + LANTERN_SHAFT_TOP_HALF_WIDTH, shaft_top),
        (DOME_CENTER_X + LANTERN_SHAFT_HALF_WIDTH, shaft_top + 8),
        (DOME_CENTER_X + LANTERN_SHAFT_HALF_WIDTH, lantern_base_y),
    ]
    palette.set_color(ctx, palette.CREAM)
    ctx.move_to(*body_points[0])
    for point in body_points[1:]:
        ctx.line_to(*point)
    ctx.close_path()
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.4)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.22)
    for offset in [-10, 0, 10]:
        ctx.rectangle(DOME_CENTER_X + offset, shaft_top + 5, 2, max(shaft_height - 10, 4))
        ctx.fill()

    cap_progress = max(0.0, (progress - 0.45) / 0.55)
    if cap_progress <= 0:
        return

    cap_height = LANTERN_CAP_HEIGHT * cap_progress
    cap_base_y = shaft_top
    cap_apex_y = cap_base_y - cap_height

    palette.set_color(ctx, palette.CREAM)
    ctx.move_to(DOME_CENTER_X - LANTERN_CAP_HALF_WIDTH, cap_base_y)
    ctx.line_to(DOME_CENTER_X, cap_apex_y)
    ctx.line_to(DOME_CENTER_X + LANTERN_CAP_HALF_WIDTH, cap_base_y)
    ctx.close_path()
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.2)
    ctx.stroke()

    sphere_progress = max(0.0, (progress - 0.72) / 0.28)
    if sphere_progress <= 0:
        return

    sphere_y = cap_apex_y - (LANTERN_SPHERE_RADIUS + 2)
    palette.set_color(ctx, palette.GOLD)
    ctx.arc(DOME_CENTER_X, sphere_y, LANTERN_SPHERE_RADIUS, 0, math.tau)
    ctx.fill()

    cross_height = LANTERN_CROSS_HEIGHT * sphere_progress
    if cross_height > 0:
        cross_top = sphere_y - LANTERN_SPHERE_RADIUS - cross_height
        palette.set_color(ctx, palette.GOLD)
        ctx.set_line_width(1.5)
        ctx.move_to(DOME_CENTER_X, sphere_y - LANTERN_SPHERE_RADIUS)
        ctx.line_to(DOME_CENTER_X, cross_top)
        ctx.stroke()

        arm_y = cross_top + cross_height * 0.45
        ctx.move_to(DOME_CENTER_X - LANTERN_CROSS_ARM, arm_y)
        ctx.line_to(DOME_CENTER_X + LANTERN_CROSS_ARM, arm_y)
        ctx.stroke()


def draw_springing_ring_overlay(ctx: cairo.Context):
    """Draw the stone cornice where the dome springs from the drum."""
    left = DOME_LEFT_X
    right = DOME_RIGHT_X
    top = DOME_BASE_Y - 2
    height = 12

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.22)
    ctx.rectangle(left + 10, top + height, right - left - 20, 6)
    ctx.fill()

    palette.set_color(ctx, palette.STONE_LIGHT)
    ctx.rectangle(left, top, right - left, height)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.4)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.GOLD, 0.12)
    ctx.rectangle(left + 18, top + 2, right - left - 36, 2)
    ctx.fill()


def draw_hoist_overview(ctx: cairo.Context):
    """Draw a simplified hoist beside the dome for the interactive explorer."""
    mast_x = HOIST_MAST_X
    mast_top = HOIST_MAST_TOP
    mast_bottom = HOIST_MAST_BOTTOM

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.32)
    ctx.set_line_width(10)
    ctx.move_to(mast_x, mast_top)
    ctx.line_to(mast_x, mast_bottom)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_LIGHT, 0.52)
    ctx.set_line_width(4)
    ctx.move_to(mast_x - HOIST_ARM_LEFT, mast_top + HOIST_PULLEY_OFFSET_Y)
    ctx.line_to(mast_x + HOIST_ARM_RIGHT, mast_top + HOIST_PULLEY_OFFSET_Y)
    ctx.stroke()

    pulley_x = mast_x + HOIST_PULLEY_OFFSET_X
    pulley_y = mast_top + HOIST_PULLEY_OFFSET_Y
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.arc(pulley_x, pulley_y, 8, 0, math.tau)
    ctx.stroke()

    ctx.move_to(pulley_x, pulley_y)
    ctx.line_to(pulley_x, pulley_y + HOIST_CRATE_DROP)
    ctx.stroke()

    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(
        pulley_x - HOIST_CRATE_WIDTH / 2,
        pulley_y + HOIST_CRATE_DROP,
        HOIST_CRATE_WIDTH,
        HOIST_CRATE_HEIGHT,
    )
    ctx.fill_preserve()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.stroke()

    gear_y = mast_bottom - HOIST_GEAR_OFFSET_Y
    gear_r = HOIST_GEAR_RADIUS
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.arc(mast_x, gear_y, gear_r, 0, math.tau)
    ctx.stroke()
    for idx in range(10):
        angle = idx * math.tau / 10
        x1 = mast_x + gear_r * math.cos(angle)
        y1 = gear_y + gear_r * math.sin(angle)
        x2 = mast_x + (gear_r + 8) * math.cos(angle)
        y2 = gear_y + (gear_r + 8) * math.sin(angle)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    beam_end_x = HOIST_BEAM_END_X
    beam_end_y = mast_bottom - 8
    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.62)
    ctx.set_line_width(4)
    ctx.move_to(mast_x, mast_bottom - 8)
    ctx.line_to(beam_end_x, beam_end_y)
    ctx.stroke()

    ox_x = HOIST_OX_X
    ox_y = beam_end_y - HOIST_OX_BASELINE_OFFSET_Y
    palette.set_color_alpha(ctx, palette.DRUM_STONE, 0.95)
    ctx.rectangle(
        ox_x - HOIST_OX_WIDTH / 2,
        ox_y - HOIST_OX_TOP_OFFSET,
        HOIST_OX_WIDTH,
        HOIST_OX_HEIGHT,
    )
    ctx.fill_preserve()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.GOLD, 0.28)
    ctx.set_dash([6, 5])
    ctx.arc(mast_x + 28, mast_bottom - 2, 88, 0.2 * math.pi, 1.55 * math.pi)
    ctx.stroke()
    ctx.set_dash([])


def render_explorer_figure() -> cairo.ImageSurface:
    """Render a static dome figure for the interactive explorer."""
    surface = create_surface()
    ctx = cairo.Context(surface)

    draw_background(ctx)

    palette.set_color_alpha(ctx, palette.PANEL, 0.62)
    _rounded_rect(ctx, 30, 28, WIDTH - 60, HEIGHT - 70, 28)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.24)
    ctx.set_line_width(1.4)
    ctx.stroke()

    _rounded_rect(ctx, 48, 46, 178, 30, 15)
    palette.set_color_alpha(ctx, palette.PANEL_ALT, 0.84)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.68)
    ctx.set_line_width(1)
    ctx.stroke()
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    palette.set_color(ctx, palette.GOLD)
    ctx.move_to(72, 65)
    ctx.show_text("Interactive Dome Explorer")

    draw_drum(ctx, 1.0, show_sidewalls=False)
    draw_dome_exterior(ctx, 1.0)
    draw_dome_cutaway(ctx, 1.0, show_ribs=True, show_chains=True, show_herringbone=True)
    draw_springing_ring_overlay(ctx)
    draw_lantern(ctx, 1.0)
    draw_hoist_overview(ctx)

    palette.set_color_alpha(ctx, palette.TEXT_MUTED, 0.9)
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    ctx.move_to(514, 536)
    ctx.show_text("Click a highlighted feature to see the related engineering detail.")

    return surface


def render_construction_frame(progress: float, phase: int) -> cairo.ImageSurface:
    """Render a single construction frame.

    progress: 0.0-1.0, construction progress within this phase.
    phase: current phase number (2, 4, 6, 8, 10, 11, 12).
    """
    surface = create_surface()
    ctx = cairo.Context(surface)

    draw_background(ctx)
    draw_title_bar(ctx, "Building Brunelleschi's Dome")
    draw_split_labels(ctx)

    drum_progress = min(1.0, progress) if phase == 2 else 1.0
    draw_drum(ctx, drum_progress)

    if phase == 2:
        dome_frac = 0.0
    elif phase == 4:
        dome_frac = progress * 0.18
    elif phase == 6:
        dome_frac = 0.18 + progress * 0.34
    elif phase == 8:
        dome_frac = 0.52 + progress * 0.16
    elif phase == 10:
        dome_frac = 0.68 + progress * 0.27
    elif phase >= 11:
        dome_frac = 0.95 + progress * 0.05
    else:
        dome_frac = 0.0

    draw_dome_exterior(ctx, dome_frac)
    draw_dome_cutaway(
        ctx,
        dome_frac,
        show_ribs=(phase >= 8),
        show_chains=(phase >= 8),
        show_herringbone=(phase >= 6),
    )
    if dome_frac > 0:
        draw_springing_ring_overlay(ctx)

    if phase >= 11:
        lantern_progress = progress if phase == 11 else 1.0
        draw_lantern(ctx, lantern_progress)

    if phase == 12:
        _rounded_rect(ctx, WIDTH - 206, 138, 142, 34, 17)
        palette.set_color_alpha(ctx, palette.PANEL_ALT, 0.88)
        ctx.fill_preserve()
        palette.set_color_alpha(ctx, palette.GOLD, 0.7)
        ctx.set_line_width(1)
        ctx.stroke()
        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10)
        palette.set_color(ctx, palette.GOLD)
        ctx.move_to(WIDTH - 182, 159)
        ctx.show_text("Florence, 1436")

    annotation = PHASE_ANNOTATIONS.get(phase, "")
    if annotation:
        draw_annotation_bar(ctx, annotation)

    return surface
