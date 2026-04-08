"""Cairo renderer for Brunelleschi's dome construction frames.

Draws the main construction view: background, title bar, dome (exterior left,
cutaway right), and annotation bar.
"""
import cairo
import palette
import geometry

WIDTH = 800
HEIGHT = 600
DOME_BASE_RADIUS = 150
DOME_CENTER_X = WIDTH // 2
DOME_BASE_Y = 460  # y-coordinate of dome base (measured from top)

# Phase annotations
PHASE_ANNOTATIONS = {
    2: "The octagonal drum rises above the cathedral walls",
    4: "Two concentric shells begin to rise — the gap between them saves weight",
    6: "Herringbone brickwork allows each course to be self-supporting",
    8: "Stone and iron chain rings resist outward thrust like hoops on a barrel",
    10: "Each ring of bricks is a complete, stable circle — no scaffolding needed",
    11: "The lantern crowns the dome, compressing the oculus ring",
    12: "Completed: the largest masonry dome ever built, standing since 1436",
}


def create_surface() -> cairo.ImageSurface:
    """Create a new 800x600 ARGB surface."""
    return cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)


def draw_background(ctx: cairo.Context):
    """Fill the canvas with the dark brown background."""
    palette.set_color(ctx, palette.BG)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()


def draw_title_bar(ctx: cairo.Context, title: str):
    """Draw the top title bar with gold text and border."""
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    palette.set_color(ctx, palette.GOLD)
    extents = ctx.text_extents(title)
    x = (WIDTH - extents.width) / 2
    ctx.move_to(x, 28)
    ctx.show_text(title)
    ctx.set_line_width(1)
    ctx.move_to(40, 40)
    ctx.line_to(WIDTH - 40, 40)
    ctx.stroke()


def draw_annotation_bar(ctx: cairo.Context, text: str):
    """Draw the bottom annotation bar with explanation text."""
    bar_y = HEIGHT - 50
    bar_height = 30
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11)
    extents = ctx.text_extents(text)
    bar_width = min(extents.width + 32, WIDTH - 40)
    bar_x = (WIDTH - bar_width) / 2

    palette.set_color(ctx, palette.ANNOTATION_BG)
    ctx.rectangle(bar_x, bar_y, bar_width, bar_height)
    ctx.fill()

    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(1)
    ctx.rectangle(bar_x, bar_y, bar_width, bar_height)
    ctx.stroke()

    palette.set_color(ctx, palette.TEXT)
    ctx.move_to(bar_x + 16, bar_y + 20)
    ctx.show_text(text)


def draw_split_labels(ctx: cairo.Context):
    """Draw 'EXTERIOR' and 'CUTAWAY' labels and the dashed center line."""
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    ctx.move_to(60, 60)
    ctx.show_text("EXTERIOR")
    ctx.move_to(WIDTH - 120, 60)
    ctx.show_text("CUTAWAY")
    ctx.set_dash([6, 4])
    ctx.set_line_width(1)
    ctx.move_to(WIDTH // 2, 45)
    ctx.line_to(WIDTH // 2, HEIGHT - 60)
    ctx.stroke()
    ctx.set_dash([])


def draw_drum(ctx: cairo.Context, progress: float):
    """Draw the octagonal drum/base that the dome sits on."""
    drum_height = 60
    visible_height = drum_height * progress
    if visible_height <= 0:
        return

    drum_top = DOME_BASE_Y - visible_height
    drum_width = DOME_BASE_RADIUS * 2 + 40

    # Cathedral walls below (always visible)
    wall_height = 80
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2 - 20, DOME_BASE_Y,
                  drum_width + 40, wall_height)
    ctx.fill()
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(2)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2 - 20, DOME_BASE_Y,
                  drum_width + 40, wall_height)
    ctx.stroke()

    # Drum
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2, drum_top, drum_width, visible_height)
    ctx.fill()
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(2)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2, drum_top, drum_width, visible_height)
    ctx.stroke()

    # Horizontal stone course lines on drum
    ctx.set_line_width(0.5)
    palette.set_color(ctx, palette.DRUM_STONE)
    for dy in range(0, int(visible_height), 12):
        y = drum_top + dy
        ctx.move_to(DOME_CENTER_X - drum_width // 2, y)
        ctx.line_to(DOME_CENTER_X + drum_width // 2, y)
        ctx.stroke()


def _get_dome_max_height():
    """Get the apex height of the dome."""
    _, apex_y = geometry.dome_profile(0.5, DOME_BASE_RADIUS)
    return apex_y


def draw_dome_exterior(ctx: cairo.Context, height_frac: float):
    """Draw the exterior (left half) of the dome up to height_frac."""
    if height_frac <= 0:
        return

    max_height = _get_dome_max_height()
    current_height = max_height * height_frac

    # Build dome outline from base to current height (left half: t in [0, 0.5])
    points = []
    num_steps = 80
    for i in range(num_steps + 1):
        t = i / num_steps * 0.5
        x, y = geometry.dome_profile(t, DOME_BASE_RADIUS)
        if y > current_height:
            # Interpolate to cutoff
            if i > 0:
                t_prev = (i - 1) / num_steps * 0.5
                x_prev, y_prev = geometry.dome_profile(t_prev, DOME_BASE_RADIUS)
                if y != y_prev:
                    frac = (current_height - y_prev) / (y - y_prev)
                    x_cut = x_prev + frac * (x - x_prev)
                    points.append((x_cut, current_height))
            break
        points.append((x, y))

    if len(points) < 2:
        return

    # Convert to screen coordinates and build closed path
    screen_points = [(DOME_CENTER_X + px, DOME_BASE_Y - py) for px, py in points]

    # Close the shape: top edge at current height to center, down to base, back to start
    top_x = screen_points[-1][0]
    top_y = DOME_BASE_Y - current_height
    screen_points.append((DOME_CENTER_X, top_y))
    screen_points.append((DOME_CENTER_X, DOME_BASE_Y))

    ctx.save()
    ctx.rectangle(0, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    # Fill with gradient
    ctx.move_to(*screen_points[0])
    for px, py in screen_points[1:]:
        ctx.line_to(px, py)
    ctx.close_path()

    grad = cairo.LinearGradient(DOME_CENTER_X, DOME_BASE_Y,
                                 DOME_CENTER_X, DOME_BASE_Y - max_height)
    grad.add_color_stop_rgb(0.0, *palette.DARK_BROWN)
    grad.add_color_stop_rgb(0.5, *palette.SIENNA)
    grad.add_color_stop_rgb(1.0, *palette.TERRACOTTA)
    ctx.set_source(grad)
    ctx.fill_preserve()

    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(2)
    ctx.stroke()

    # Brick course lines
    course_spacing = 6
    for cy in range(0, int(current_height), course_spacing):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        screen_y = DOME_BASE_Y - cy
        palette.set_color(ctx, palette.RIB_DARK)
        ctx.set_line_width(0.3)
        ctx.move_to(DOME_CENTER_X + x_left, screen_y)
        ctx.line_to(DOME_CENTER_X, screen_y)
        ctx.stroke()

    ctx.restore()


def draw_dome_cutaway(ctx: cairo.Context, height_frac: float,
                       show_ribs: bool = False, show_chains: bool = False,
                       show_herringbone: bool = False):
    """Draw the cutaway (right half) showing inner/outer shells, ribs, chains."""
    if height_frac <= 0:
        return

    max_height = _get_dome_max_height()
    current_height = max_height * height_frac

    outer_thickness = DOME_BASE_RADIUS * 0.12
    inner_thickness = DOME_BASE_RADIUS * 0.15
    gap = DOME_BASE_RADIUS * 0.08

    ctx.save()
    ctx.rectangle(WIDTH // 2, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    # Draw shells as filled strips
    for cy in range(0, int(current_height), 2):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy

        # Outer shell
        outer_left = DOME_CENTER_X + x_right - outer_thickness
        outer_right_edge = DOME_CENTER_X + x_right
        palette.set_color(ctx, palette.SIENNA)
        ctx.rectangle(max(DOME_CENTER_X, outer_left), screen_y,
                      outer_right_edge - max(DOME_CENTER_X, outer_left), 2)
        ctx.fill()

        # Inner shell
        inner_right = DOME_CENTER_X + x_right - outer_thickness - gap
        inner_left = inner_right - inner_thickness
        if inner_right > DOME_CENTER_X:
            palette.set_color(ctx, palette.TERRACOTTA)
            ctx.rectangle(max(DOME_CENTER_X, inner_left), screen_y,
                          inner_right - max(DOME_CENTER_X, inner_left), 2)
            ctx.fill()

    # Outlines for shells
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    # Trace outer shell edges
    outer_pts_right = []
    outer_pts_left = []
    inner_pts_right = []
    inner_pts_left = []
    for cy in range(0, int(current_height), 3):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy
        outer_pts_right.append((DOME_CENTER_X + x_right, screen_y))
        outer_pts_left.append((DOME_CENTER_X + x_right - outer_thickness, screen_y))
        ir = DOME_CENTER_X + x_right - outer_thickness - gap
        il = ir - inner_thickness
        inner_pts_right.append((ir, screen_y))
        inner_pts_left.append((il, screen_y))

    for pts in [outer_pts_right, outer_pts_left, inner_pts_right, inner_pts_left]:
        if len(pts) >= 2:
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.stroke()

    # Herringbone pattern on outer shell face
    if show_herringbone:
        brick_h = 6
        brick_w = 10
        for cy in range(0, int(current_height), brick_h):
            x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            if x_right <= 0:
                continue
            screen_y = DOME_BASE_Y - cy
            shell_left = int(DOME_CENTER_X + x_right - outer_thickness)
            shell_right = int(DOME_CENTER_X + x_right)
            row = cy // brick_h
            col_idx = 0
            for bx in range(max(shell_left, DOME_CENTER_X), shell_right, brick_w):
                if (row + col_idx) % 5 == 0:
                    # Vertical spine brick
                    palette.set_color(ctx, palette.DARK_BROWN)
                    vw = max(brick_w // 3, 2)
                    ctx.rectangle(bx + brick_w // 3, screen_y - brick_h, vw, brick_h)
                    ctx.fill()
                col_idx += 1

    # Chain rings
    if show_chains:
        chain_interval = max_height / 5
        for i in range(1, 5):
            cy = chain_interval * i
            if cy > current_height:
                break
            x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            screen_y = DOME_BASE_Y - cy
            palette.set_color(ctx, palette.GOLD)
            ctx.set_line_width(3)
            ctx.move_to(DOME_CENTER_X, screen_y)
            ctx.line_to(DOME_CENTER_X + x_right, screen_y)
            ctx.stroke()
            # Small label on first visible chain
            if i == 1:
                ctx.set_font_size(8)
                ctx.move_to(DOME_CENTER_X + x_right + 4, screen_y + 3)
                ctx.show_text("chain")

    # Major ribs
    if show_ribs:
        palette.set_color(ctx, palette.RIB_DARK)
        ctx.set_line_width(4)
        for rib_frac in [0.2, 0.5, 0.8]:
            points = []
            for cy in range(0, int(current_height), 4):
                x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
                if x_right <= 0:
                    continue
                rib_x = DOME_CENTER_X + x_right * rib_frac
                points.append((rib_x, DOME_BASE_Y - cy))
            if len(points) >= 2:
                ctx.move_to(*points[0])
                for p in points[1:]:
                    ctx.line_to(*p)
                ctx.stroke()

    ctx.restore()


def draw_lantern(ctx: cairo.Context, progress: float = 1.0):
    """Draw the lantern atop the completed dome."""
    max_height = _get_dome_max_height()
    lantern_base_y = DOME_BASE_Y - max_height
    lantern_width = 30
    lantern_height = int(50 * progress)

    # Oculus ring
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - lantern_width, lantern_base_y - 8,
                  lantern_width * 2, 8)
    ctx.fill()
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(1.5)
    ctx.rectangle(DOME_CENTER_X - lantern_width, lantern_base_y - 8,
                  lantern_width * 2, 8)
    ctx.stroke()

    if lantern_height <= 0:
        return

    # Lantern body
    body_w = lantern_width * 1.2
    body_top = lantern_base_y - 8 - lantern_height
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - body_w / 2, body_top, body_w, lantern_height)
    ctx.fill()
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(1.5)
    ctx.rectangle(DOME_CENTER_X - body_w / 2, body_top, body_w, lantern_height)
    ctx.stroke()

    # Lantern cap (cone)
    if progress >= 0.8:
        palette.set_color(ctx, palette.DARK_BROWN)
        ctx.move_to(DOME_CENTER_X - body_w / 2, body_top)
        ctx.line_to(DOME_CENTER_X, body_top - 25)
        ctx.line_to(DOME_CENTER_X + body_w / 2, body_top)
        ctx.close_path()
        ctx.fill()


def render_construction_frame(progress: float, phase: int) -> cairo.ImageSurface:
    """Render a single construction frame.

    progress: 0.0-1.0, construction progress within this phase.
    phase: current phase number (2, 4, 6, 8, 10, 11, 12).
    """
    surface = create_surface()
    ctx = cairo.Context(surface)

    draw_background(ctx)
    draw_title_bar(ctx, "BUILDING BRUNELLESCHI'S DOME  1420-1436")
    draw_split_labels(ctx)

    # Drum
    drum_progress = min(1.0, progress) if phase == 2 else 1.0
    draw_drum(ctx, drum_progress)

    # Dome height depends on phase
    if phase == 2:
        dome_frac = 0.0
    elif phase == 4:
        dome_frac = progress * 0.15
    elif phase == 6:
        dome_frac = 0.15 + progress * 0.35
    elif phase == 8:
        dome_frac = 0.50 + progress * 0.15
    elif phase == 10:
        dome_frac = 0.65 + progress * 0.30
    elif phase >= 11:
        dome_frac = 0.95 + progress * 0.05
    else:
        dome_frac = 0.0

    draw_dome_exterior(ctx, dome_frac)
    draw_dome_cutaway(
        ctx, dome_frac,
        show_ribs=(phase >= 8),
        show_chains=(phase >= 8),
        show_herringbone=(phase >= 6),
    )

    if phase >= 11:
        lantern_progress = progress if phase == 11 else 1.0
        draw_lantern(ctx, lantern_progress)

    annotation = PHASE_ANNOTATIONS.get(phase, "")
    if annotation:
        draw_annotation_bar(ctx, annotation)

    return surface
