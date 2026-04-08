"""Detail inset frame renderers for Brunelleschi's dome animation.

Each function renders a single teaching inset frame explaining one
engineering innovation. All insets share the warm palette and a common
layout: DETAIL header, diagram area (upper 2/3), explanation text box
(lower 1/3), footer.
"""
import math
import cairo
import palette
import renderer
import geometry


def _rounded_rect(ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float):
    """Create a rounded rectangle path."""
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -1.5708, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 1.5708)
    ctx.arc(x + r, y + h - r, r, 1.5708, 3.14159)
    ctx.arc(x + r, y + r, r, 3.14159, 4.71239)
    ctx.close_path()


def _draw_inset_template(ctx: cairo.Context, title: str, explanation: str):
    """Draw the shared inset frame template."""
    renderer.draw_background(ctx)

    # Header
    header_x, header_y = 34, 24
    header_w, header_h = renderer.WIDTH - 68, 60
    _rounded_rect(ctx, header_x, header_y, header_w, header_h, 16)
    palette.set_color_alpha(ctx, palette.PANEL, 0.92)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.65)
    ctx.set_line_width(1.2)
    ctx.stroke()

    ctx.select_font_face("serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(23)
    palette.set_color(ctx, palette.TEXT)
    header_text = title
    extents = ctx.text_extents(header_text)
    ctx.move_to((renderer.WIDTH - extents.width) / 2, header_y + 26)
    ctx.show_text(header_text)

    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    badge = "DETAIL CARD"
    badge_extents = ctx.text_extents(badge)
    ctx.move_to((renderer.WIDTH - badge_extents.width) / 2, header_y + 44)
    ctx.show_text(badge)

    # Diagram panel
    panel_x, panel_y = 52, 100
    panel_w, panel_h = renderer.WIDTH - 104, 298
    _rounded_rect(ctx, panel_x, panel_y, panel_w, panel_h, 24)
    palette.set_color_alpha(ctx, palette.PANEL_ALT, 0.62)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.26)
    ctx.set_line_width(1.0)
    ctx.stroke()

    # Explanation box
    box_x, box_y = 60, 422
    box_w, box_h = renderer.WIDTH - 120, 132
    _rounded_rect(ctx, box_x, box_y, box_w, box_h, 18)
    palette.set_color_alpha(ctx, palette.ANNOTATION_BG, 0.96)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.GOLD, 0.78)
    ctx.set_line_width(1.2)
    ctx.stroke()

    # Wrapped explanation text
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(13)
    palette.set_color(ctx, palette.TEXT)
    _draw_wrapped_text(ctx, explanation, box_x + 18, box_y + 42, box_w - 36, line_height=20)

    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    ctx.move_to(box_x + 18, box_y + 22)
    ctx.show_text("ENGINEERING IDEA")

    # Footer
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.TEXT_MUTED)
    footer = "returning to construction..."
    extents = ctx.text_extents(footer)
    ctx.move_to((renderer.WIDTH - extents.width) / 2, renderer.HEIGHT - 18)
    ctx.show_text(footer)


def _draw_wrapped_text(ctx: cairo.Context, text: str, x: float, y: float,
                        max_width: float, line_height: float = 18):
    """Draw text with simple word-wrapping."""
    words = text.split()
    line = ""
    cy = y
    for word in words:
        test = f"{line} {word}".strip()
        extents = ctx.text_extents(test)
        if extents.width > max_width and line:
            ctx.move_to(x, cy)
            ctx.show_text(line)
            line = word
            cy += line_height
        else:
            line = test
    if line:
        ctx.move_to(x, cy)
        ctx.show_text(line)


def render_arch_comparison() -> cairo.ImageSurface:
    """Inset 1: Semicircular vs pointed-fifth arch comparison."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(
        ctx,
        "Pointed-Fifth Arch",
        "A semicircular dome pushes hard outward at the springing, so builders normally need heavy timber centering. "
        "Brunelleschi's pointed profile redirects more force downward, allowing the masonry rings to stabilize themselves "
        "as they rise. Each arc center sits at four-fifths of the span from the opposite side.",
    )

    base_y = 338
    arch_radius = 96
    card_y = 128
    card_w = 276
    card_h = 214

    cards = [
        (90, "Semicircular arch", "Strong lateral thrust", "Needs centering", palette.SIENNA),
        (434, "Pointed-fifth arch", "More vertical thrust", "Self-supporting", palette.TERRACOTTA),
    ]

    for x, label, force_label, verdict, arch_color in cards:
        _rounded_rect(ctx, x, card_y, card_w, card_h, 22)
        palette.set_color_alpha(ctx, palette.PANEL, 0.74)
        ctx.fill_preserve()
        palette.set_color_alpha(ctx, palette.GOLD, 0.24)
        ctx.set_line_width(1)
        ctx.stroke()

        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        palette.set_color(ctx, palette.TEXT)
        ext = ctx.text_extents(label)
        ctx.move_to(x + (card_w - ext.width) / 2, card_y + 24)
        ctx.show_text(label)

        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10)
        palette.set_color(ctx, palette.GOLD)
        force_ext = ctx.text_extents(force_label)
        ctx.move_to(x + (card_w - force_ext.width) / 2, card_y + 42)
        ctx.show_text(force_label)

        center_x = x + card_w / 2
        palette.set_color(ctx, arch_color)
        ctx.set_line_width(4)

        if "Semicircular" in label:
            ctx.arc(center_x, base_y, arch_radius, math.pi, 0)
            ctx.stroke()
            ctx.set_line_width(2)
            ctx.move_to(center_x - arch_radius, base_y)
            ctx.line_to(center_x + arch_radius, base_y)
            ctx.stroke()

            palette.set_color_alpha(ctx, palette.GOLD, 0.75)
            ctx.set_line_width(2)
            for dx in [-1, 1]:
                ax = center_x + dx * (arch_radius - 8)
                ctx.move_to(ax, base_y - 10)
                ctx.line_to(ax + dx * 34, base_y - 10)
                ctx.line_to(ax + dx * 26, base_y - 16)
                ctx.move_to(ax + dx * 34, base_y - 10)
                ctx.line_to(ax + dx * 26, base_y - 4)
                ctx.stroke()

            palette.set_color_alpha(ctx, palette.STONE_SHADOW, 0.45)
            ctx.set_dash([4, 4])
            for idx in range(-3, 4):
                sx = center_x + idx * 24
                ctx.move_to(sx, base_y)
                ctx.line_to(sx, base_y - arch_radius + abs(idx) * 11)
                ctx.stroke()
            ctx.set_dash([])
        else:
            points = []
            for i in range(81):
                t = i / 80.0
                px, py = geometry.dome_profile(t, arch_radius)
                points.append((center_x + px, base_y - py))
            ctx.move_to(*points[0])
            for point in points[1:]:
                ctx.line_to(*point)
            ctx.stroke()
            ctx.set_line_width(2)
            ctx.move_to(center_x - arch_radius, base_y)
            ctx.line_to(center_x + arch_radius, base_y)
            ctx.stroke()

            palette.set_color_alpha(ctx, palette.GOLD, 0.75)
            ctx.set_line_width(2)
            for dx in [-1, 1]:
                ax = center_x + dx * (arch_radius - 4)
                end_x = ax + dx * 10
                end_y = base_y + 36
                ctx.move_to(ax, base_y - 8)
                ctx.line_to(end_x, end_y)
                ctx.line_to(end_x - 5, end_y - 8)
                ctx.move_to(end_x, end_y)
                ctx.line_to(end_x + 5, end_y - 8)
                ctx.stroke()

            palette.set_color_alpha(ctx, palette.TEXT_MUTED, 0.55)
            ctx.set_line_width(1)
            ctx.move_to(center_x, base_y - arch_radius - 30)
            ctx.line_to(center_x, base_y + 6)
            ctx.stroke()

        ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11)
        verdict_ext = ctx.text_extents(verdict)
        palette.set_color(ctx, palette.TEXT)
        ctx.move_to(x + (card_w - verdict_ext.width) / 2, card_y + card_h - 18)
        ctx.show_text(verdict)

    palette.set_color_alpha(ctx, palette.GOLD, 0.85)
    _rounded_rect(ctx, 342, 204, 116, 50, 16)
    ctx.fill_preserve()
    palette.set_color_alpha(ctx, palette.PANEL, 0.9)
    ctx.set_line_width(1)
    ctx.stroke()
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.PANEL)
    note = "less outward\npush"
    for idx, line in enumerate(note.splitlines()):
        ext = ctx.text_extents(line)
        ctx.move_to(342 + (116 - ext.width) / 2, 223 + idx * 13)
        ctx.show_text(line)

    return surface


def render_herringbone() -> cairo.ImageSurface:
    """Inset 2: Herringbone brickwork close-up."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "HERRINGBONE BRICKWORK",
        "Bricks are laid mostly horizontal, but with vertical bricks inserted "
        "at regular intervals. These vertical 'spine' bricks act as teeth that "
        "lock each horizontal course in place, preventing wet mortar from "
        "sliding before it sets. This technique allowed Brunelleschi to build "
        "without centering — temporary wooden scaffolding from below.")

    # Draw a zoomed brick grid
    start_x, start_y = 120, 126
    brick_w, brick_h = 50, 18
    rows = 18
    cols = 11

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * brick_w + (row % 2) * (brick_w // 2)
            y = start_y + row * brick_h

            if y > 392:
                continue
            if x > renderer.WIDTH - 40:
                continue

            is_spine = (col % 4 == 2)

            if is_spine:
                # Vertical spine brick (darker, spans ~2 rows visually)
                palette.set_color(ctx, palette.DARK_BROWN)
                vw = brick_w // 3
                vh = brick_h * 2 - 2
                ctx.rectangle(x + brick_w // 3, y, vw, vh)
                ctx.fill()
                # Outline
                palette.set_color(ctx, palette.RIB_DARK)
                ctx.set_line_width(0.8)
                ctx.rectangle(x + brick_w // 3, y, vw, vh)
                ctx.stroke()
            else:
                # Horizontal brick with slight color variation
                color = palette.TERRACOTTA if (row + col) % 3 != 0 else palette.SIENNA
                palette.set_color(ctx, color)
                ctx.rectangle(x + 1, y + 1, brick_w - 2, brick_h - 2)
                ctx.fill()
                palette.set_color(ctx, palette.RIB_DARK)
                ctx.set_line_width(0.5)
                ctx.rectangle(x + 1, y + 1, brick_w - 2, brick_h - 2)
                ctx.stroke()

    # Annotation arrows pointing to vertical bricks
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    # Arrow from label to a spine brick
    spine_x = start_x + 2 * brick_w + brick_w // 2
    ctx.set_font_size(11)

    # Top label
    palette.set_color(ctx, palette.GOLD)
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(11)
    label = "vertical 'spine' bricks lock horizontal courses in place"
    ext = ctx.text_extents(label)
    ctx.move_to((renderer.WIDTH - ext.width) / 2, 418)
    ctx.show_text(label)

    return surface


def render_chain_rings() -> cairo.ImageSurface:
    """Inset 3: Chain rings cross-section."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "CHAIN RINGS",
        "At regular intervals, Brunelleschi embedded horizontal tension rings "
        "of sandstone blocks linked with iron clamps, reinforced with wooden "
        "tie-beams. These act like hoops on a barrel — resisting the outward "
        "thrust that would otherwise push the dome apart. Four major "
        "stone-and-iron chains plus additional wooden chains between them.")

    cx = renderer.WIDTH // 2
    base_y = 400
    section_w = 340
    section_h = 310

    # Draw dome wall cross-section (radial slice)
    shell_w = 35

    # Left outer shell
    lo_x = cx - section_w // 2
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(lo_x, base_y - section_h, shell_w, section_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(lo_x, base_y - section_h, shell_w, section_h)
    ctx.stroke()

    # Left inner shell
    li_x = lo_x + shell_w + 45
    inner_w = 45
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.rectangle(li_x, base_y - section_h, inner_w, section_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(li_x, base_y - section_h, inner_w, section_h)
    ctx.stroke()

    # Right inner shell
    ri_x = cx + section_w // 2 - shell_w - 45 - inner_w
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.rectangle(ri_x, base_y - section_h, inner_w, section_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.rectangle(ri_x, base_y - section_h, inner_w, section_h)
    ctx.stroke()

    # Right outer shell
    ro_x = cx + section_w // 2 - shell_w
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(ro_x, base_y - section_h, shell_w, section_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.rectangle(ro_x, base_y - section_h, shell_w, section_h)
    ctx.stroke()

    # Gap labels
    palette.set_color(ctx, palette.TEXT)
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(9)
    ctx.move_to(lo_x + shell_w + 10, base_y - section_h // 2)
    ctx.show_text("gap")
    ctx.move_to(ro_x - 30, base_y - section_h // 2)
    ctx.show_text("gap")

    # Shell labels at bottom
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(9)
    ctx.move_to(lo_x, base_y + 14)
    ctx.show_text("outer")
    ctx.move_to(li_x + 5, base_y + 14)
    ctx.show_text("inner")
    ctx.move_to(ri_x + 5, base_y + 14)
    ctx.show_text("inner")
    ctx.move_to(ro_x, base_y + 14)
    ctx.show_text("outer")

    # Chain rings — horizontal bands spanning the full section
    chain_positions = [0.2, 0.4, 0.6, 0.8]
    for idx, frac in enumerate(chain_positions):
        chain_y = base_y - section_h * frac
        chain_h = 12

        # Stone block band
        palette.set_color(ctx, palette.CREAM)
        ctx.rectangle(lo_x - 5, chain_y - chain_h // 2,
                      section_w + 10, chain_h)
        ctx.fill()

        # Gold border (iron clamps)
        palette.set_color(ctx, palette.GOLD)
        ctx.set_line_width(2)
        ctx.rectangle(lo_x - 5, chain_y - chain_h // 2,
                      section_w + 10, chain_h)
        ctx.stroke()

        # Iron clamp marks (small rectangles)
        for cx_mark in range(lo_x + 20, lo_x + section_w, 40):
            palette.set_color(ctx, palette.RIB_DARK)
            ctx.rectangle(cx_mark, chain_y - 2, 8, 4)
            ctx.fill()

    # Label one chain
    palette.set_color(ctx, palette.GOLD)
    ctx.set_font_size(10)
    ctx.move_to(cx + section_w // 2 + 12, base_y - section_h * 0.2 + 4)
    ctx.show_text("stone + iron")
    ctx.move_to(cx + section_w // 2 + 12, base_y - section_h * 0.2 + 16)
    ctx.show_text("chain ring")

    return surface


def render_ox_hoist() -> cairo.ImageSurface:
    """Inset 4: Brunelleschi's ox-hoist crane."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "OX-HOIST CRANE",
        "Brunelleschi invented a reversible hoist powered by oxen walking in "
        "a circle. A clever gear mechanism allowed the load direction to "
        "reverse without unhitching and turning the oxen around — the first "
        "known reversible gear. This crane lifted over 70 million pounds of "
        "material to the top of the dome.")

    cx = renderer.WIDTH // 2
    base_y = 380

    # Central vertical shaft
    shaft_w = 14
    shaft_h = 270
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(cx - shaft_w // 2, base_y - shaft_h, shaft_w, shaft_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1.5)
    ctx.rectangle(cx - shaft_w // 2, base_y - shaft_h, shaft_w, shaft_h)
    ctx.stroke()

    # Horizontal arm at top
    arm_w = 180
    arm_h = 10
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(cx - arm_w // 2, base_y - shaft_h, arm_w, arm_h)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.rectangle(cx - arm_w // 2, base_y - shaft_h, arm_w, arm_h)
    ctx.stroke()

    # Rope from right arm end
    rope_start_x = cx + arm_w // 2 - 10
    rope_start_y = base_y - shaft_h + arm_h
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.move_to(rope_start_x, rope_start_y)
    ctx.line_to(rope_start_x, rope_start_y + 80)
    ctx.stroke()

    # Load box
    load_y = rope_start_y + 80
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(rope_start_x - 18, load_y, 36, 28)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(rope_start_x - 18, load_y, 36, 28)
    ctx.stroke()
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(9)
    ctx.move_to(rope_start_x - 10, load_y + 18)
    ctx.show_text("load")

    # Pulley wheel at top
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.arc(rope_start_x, rope_start_y, 8, 0, 2 * math.pi)
    ctx.stroke()

    # Gear mechanism at shaft base
    gear_y = base_y - 45
    gear_r = 28
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2.5)
    ctx.arc(cx, gear_y, gear_r, 0, 2 * math.pi)
    ctx.stroke()

    # Gear teeth
    for i in range(10):
        angle = i * 2 * math.pi / 10
        x1 = cx + gear_r * math.cos(angle)
        y1 = gear_y + gear_r * math.sin(angle)
        x2 = cx + (gear_r + 8) * math.cos(angle)
        y2 = gear_y + (gear_r + 8) * math.sin(angle)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    # Inner gear (smaller)
    ctx.set_line_width(1.5)
    ctx.arc(cx, gear_y, gear_r * 0.5, 0, 2 * math.pi)
    ctx.stroke()

    # "Reversible gear" label
    palette.set_color(ctx, palette.GOLD)
    ctx.set_font_size(10)
    ctx.move_to(cx + gear_r + 15, gear_y + 4)
    ctx.show_text("reversible gear")

    # Ox walking circle
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.set_dash([5, 4])
    ox_radius = 85
    ctx.arc(cx, base_y + 10, ox_radius, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_dash([])

    # Horizontal beam from shaft to ox
    ox_angle = -0.3
    ox_x = cx + ox_radius * math.cos(ox_angle)
    ox_y = base_y + 10 + ox_radius * math.sin(ox_angle)
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(4)
    ctx.move_to(cx, base_y + 10)
    ctx.line_to(ox_x, ox_y)
    ctx.stroke()

    # Ox (simplified rectangle)
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(ox_x - 18, ox_y - 14, 36, 22)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(ox_x - 18, ox_y - 14, 36, 22)
    ctx.stroke()
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(10)
    ctx.move_to(ox_x - 7, ox_y + 2)
    ctx.show_text("ox")

    # Walking direction arrow (arc with arrowhead)
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(1.5)
    ctx.arc(cx, base_y + 10, ox_radius + 12, -0.5, 0.3)
    ctx.stroke()
    # Arrowhead
    end_x = cx + (ox_radius + 12) * math.cos(0.3)
    end_y = (base_y + 10) + (ox_radius + 12) * math.sin(0.3)
    ctx.move_to(end_x, end_y)
    ctx.line_to(end_x - 8, end_y - 6)
    ctx.move_to(end_x, end_y)
    ctx.line_to(end_x + 2, end_y - 9)
    ctx.stroke()

    return surface
