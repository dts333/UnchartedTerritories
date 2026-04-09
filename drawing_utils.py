"""Shared Cairo drawing helpers."""


def rounded_rect(ctx, x: float, y: float, w: float, h: float, r: float):
    """Create a rounded rectangle path."""
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -1.5708, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 1.5708)
    ctx.arc(x + r, y + h - r, r, 1.5708, 3.14159)
    ctx.arc(x + r, y + r, r, 3.14159, 4.71239)
    ctx.close_path()


def wrap_text(ctx, text: str, max_width: float) -> list[str]:
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


def draw_wrapped_text(
    ctx,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float,
    max_lines: int | None = None,
):
    """Draw wrapped text with optional line limiting."""
    lines = wrap_text(ctx, text, max_width)
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
