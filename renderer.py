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


def draw_drum(ctx: cairo.Context, progress: float):
    """Draw the octagonal drum and cathedral body beneath it."""
    visible_height = 72 * progress

    podium_x = DOME_CENTER_X - 208
    podium_y = DOME_BASE_Y + 10
    podium_w = 416
    podium_h = 78
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(podium_x, podium_y, podium_w, podium_h)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(2)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.15)
    for x in range(podium_x + 16, podium_x + podium_w, 36):
        ctx.rectangle(x, podium_y + 4, 2, podium_h - 8)
        ctx.fill()

    wing_y = DOME_BASE_Y - 16
    wing_h = 70
    for wing_x in [DOME_CENTER_X - 170, DOME_CENTER_X + 50]:
        palette.set_color(ctx, palette.STONE_LIGHT)
        ctx.rectangle(wing_x, wing_y, 120, wing_h)
        ctx.fill_preserve()
        palette.set_color(ctx, palette.STONE_SHADOW)
        ctx.set_line_width(1.6)
        ctx.stroke()
        palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.28)
        for offset in range(0, wing_h, 15):
            ctx.rectangle(wing_x + 1, wing_y + offset, 118, 2)
            ctx.fill()

    if visible_height <= 0:
        return

    drum_top = DOME_BASE_Y - visible_height
    drum_w = 220
    drum_x = DOME_CENTER_X - drum_w / 2

    palette.set_color(ctx, palette.STONE_LIGHT)
    ctx.rectangle(drum_x, drum_top, drum_w, visible_height)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(2)
    ctx.stroke()

    side_facets = [
        [(drum_x, drum_top), (drum_x - 24, drum_top + 12), (drum_x - 24, DOME_BASE_Y), (drum_x, DOME_BASE_Y)],
        [(drum_x + drum_w, drum_top), (drum_x + drum_w + 24, drum_top + 12), (drum_x + drum_w + 24, DOME_BASE_Y), (drum_x + drum_w, DOME_BASE_Y)],
    ]
    for idx, facet in enumerate(side_facets):
        palette.set_color(ctx, palette.CREAM if idx == 0 else palette.DRUM_STONE)
        ctx.move_to(*facet[0])
        for point in facet[1:]:
            ctx.line_to(*point)
        ctx.close_path()
        ctx.fill_preserve()
        palette.set_color(ctx, palette.STONE_SHADOW)
        ctx.set_line_width(1.5)
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
        for center_x in [DOME_CENTER_X - 56, DOME_CENTER_X, DOME_CENTER_X + 56]:
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
    lantern_height = 42 * progress
    drum_w = 58

    palette.set_color(ctx, palette.STONE_LIGHT)
    ctx.rectangle(DOME_CENTER_X - drum_w / 2, lantern_base_y - 10, drum_w, 10)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.5)
    ctx.stroke()

    if lantern_height <= 0:
        return

    body_w = 46
    body_top = lantern_base_y - 10 - lantern_height
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - body_w / 2, body_top, body_w, lantern_height)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.STONE_SHADOW)
    ctx.set_line_width(1.4)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.22)
    for offset in [10, 22, 34]:
        ctx.rectangle(DOME_CENTER_X - body_w / 2 + offset, body_top + 4, 2, lantern_height - 8)
        ctx.fill()

    if progress >= 0.75:
        palette.set_color(ctx, palette.DARK_BROWN)
        ctx.move_to(DOME_CENTER_X - body_w / 2 - 4, body_top + 2)
        ctx.line_to(DOME_CENTER_X, body_top - 18)
        ctx.line_to(DOME_CENTER_X + body_w / 2 + 4, body_top + 2)
        ctx.close_path()
        ctx.fill()


def draw_hoist_overview(ctx: cairo.Context):
    """Draw a simplified hoist beside the dome for the interactive explorer."""
    mast_x = 660
    mast_top = 138
    mast_bottom = 438

    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.32)
    ctx.set_line_width(10)
    ctx.move_to(mast_x, mast_top)
    ctx.line_to(mast_x, mast_bottom)
    ctx.stroke()

    palette.set_color_alpha(ctx, palette.STONE_LIGHT, 0.52)
    ctx.set_line_width(4)
    ctx.move_to(mast_x - 58, mast_top + 18)
    ctx.line_to(mast_x + 34, mast_top + 18)
    ctx.stroke()

    pulley_x = mast_x + 26
    pulley_y = mast_top + 18
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.arc(pulley_x, pulley_y, 8, 0, math.tau)
    ctx.stroke()

    ctx.move_to(pulley_x, pulley_y)
    ctx.line_to(pulley_x, pulley_y + 116)
    ctx.stroke()

    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(pulley_x - 16, pulley_y + 116, 32, 26)
    ctx.fill_preserve()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.stroke()

    gear_y = mast_bottom - 42
    gear_r = 24
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

    beam_end_x = 724
    beam_end_y = mast_bottom - 8
    palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.62)
    ctx.set_line_width(4)
    ctx.move_to(mast_x, mast_bottom - 8)
    ctx.line_to(beam_end_x, beam_end_y)
    ctx.stroke()

    ox_x = 742
    ox_y = beam_end_y - 6
    palette.set_color_alpha(ctx, palette.DRUM_STONE, 0.95)
    ctx.rectangle(ox_x - 22, ox_y - 14, 44, 24)
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

    draw_drum(ctx, 1.0)
    draw_dome_exterior(ctx, 1.0)
    draw_dome_cutaway(ctx, 1.0, show_ribs=True, show_chains=True, show_herringbone=True)
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
