# Brunelleschi's Dome Construction GIF — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate an animated GIF that teaches viewers how Brunelleschi's dome was constructed, frame by frame, with four detailed teaching insets.

**Architecture:** Python script pipeline — `palette.py` defines colors, `geometry.py` computes dome math, `renderer.py` draws construction frames with Cairo, `insets.py` draws four detail frames, and `dome.py` orchestrates frame generation and GIF assembly with imageio.

**Tech Stack:** Python 3, pycairo, imageio[pillow]

**Spec:** `docs/superpowers/specs/2026-04-08-brunelleschi-dome-gif-design.md`

---

## Chunk 1: Project Setup, Palette, and Geometry

### Task 1: Project scaffolding and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repo and create requirements.txt**

```bash
cd /Users/dannyswift/Projects/uncharted_territories
git init
```

```
# requirements.txt
pycairo>=1.25.0
imageio[pillow]>=2.34.0
```

- [ ] **Step 2: Create .gitignore**

```
# .gitignore
frames/
output/
__pycache__/
*.pyc
.superpowers/
```

- [ ] **Step 3: Install dependencies and verify Cairo works**

```bash
pip install -r requirements.txt
python -c "import cairo; print(cairo.version)"
```

Expected: prints Cairo version without error.

- [ ] **Step 4: Create output directories**

```bash
mkdir -p frames output
```

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "chore: initial project setup with pycairo and imageio deps"
```

---

### Task 2: Palette module

**Files:**
- Create: `palette.py`
- Create: `tests/test_palette.py`

- [ ] **Step 1: Write test for palette constants**

```python
# tests/test_palette.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_palette.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'palette'`

- [ ] **Step 3: Implement palette.py**

```python
# palette.py
"""Color palette for Brunelleschi's dome animation.

All colors are (r, g, b) tuples with values 0.0–1.0, ready for Cairo's set_source_rgb.
Hex references in comments for visual identification.
"""

# Background
BG = (0.165, 0.122, 0.078)            # #2a1f14

# Dome surfaces
TERRACOTTA = (0.769, 0.400, 0.227)    # #c4663a
SIENNA = (0.627, 0.322, 0.176)        # #a0522d
DARK_BROWN = (0.545, 0.271, 0.075)    # #8b4513

# Structural
DRUM_STONE = (0.478, 0.384, 0.282)    # #7a6248
RIB_DARK = (0.353, 0.275, 0.220)      # #5a4638

# Accents
GOLD = (0.769, 0.639, 0.353)          # #c4a35a
CREAM = (0.831, 0.773, 0.663)         # #d4c5a9
TEXT = (0.910, 0.835, 0.718)          # #e8d5b7

# UI elements
ANNOTATION_BG = (0.227, 0.184, 0.122) # #3a2f1f


def set_color(ctx, color):
    """Set Cairo source color from a palette tuple."""
    ctx.set_source_rgb(*color)
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_palette.py -v
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add palette.py tests/test_palette.py
git commit -m "feat: add palette module with Florentine color constants"
```

---

### Task 3: Geometry module — dome profile

**Files:**
- Create: `geometry.py`
- Create: `tests/test_geometry.py`

- [ ] **Step 1: Write tests for dome_profile**

The pointed-fifth arch: two circular arcs whose centers are each at 4/5 of the base diameter from the opposite side. For a dome with base radius R (diameter 2R), the left arc center is at x = +0.6R (4/5 of diameter from left = 1.6R, centered at origin = 0.6R), and the right arc center is at x = -0.6R. The arc radius is the distance from each center to the opposite base corner.

```python
# tests/test_geometry.py
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
    """Profile at t=0.5 should be at x≈0 and y > 0 (above base)."""
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
    assert apex_y > 100, f"Apex height {apex_y} is not greater than radius 100 — not a pointed arch"


def test_dome_profile_at_height():
    """dome_profile_at_height should return left and right x for a given y."""
    x_left, x_right = geometry.dome_profile_at_height(0, 100)
    assert abs(x_left - (-100)) < 1.0
    assert abs(x_right - 100) < 1.0
    # At some mid-height, dome should be narrower than base
    x_left_mid, x_right_mid = geometry.dome_profile_at_height(80, 100)
    assert x_right_mid < 100, "Dome should narrow above base"
    assert x_left_mid > -100, "Dome should narrow above base"


def test_octagon_points():
    """Should return 8 points on a circle of given radius."""
    points = geometry.octagon_points(100)
    assert len(points) == 8
    for x, y in points:
        dist = math.sqrt(x**2 + y**2)
        assert abs(dist - 100) < 0.1, f"Point ({x},{y}) not on circle: dist={dist}"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_geometry.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'geometry'`

- [ ] **Step 3: Implement geometry.py**

```python
# geometry.py
"""Parametric geometry for Brunelleschi's dome.

The dome uses a pointed-fifth arch profile: two circular arcs whose centers
are each placed at 4/5 of the base diameter from the opposite side.
"""
import math


def dome_profile(t: float, base_radius: float) -> tuple[float, float]:
    """Return (x, y) on the dome profile for parameter t in [0, 1].

    t=0: left base (-base_radius, 0)
    t=0.5: apex (~0, max_height)
    t=1: right base (base_radius, 0)
    """
    diameter = 2 * base_radius
    # Arc centers at 4/5 of diameter from opposite side
    # Right arc center: 4/5 * diameter from left = -base_radius + 0.8 * diameter
    cx_right = -base_radius + 0.8 * diameter  # = 0.6 * base_radius
    cx_left = base_radius - 0.8 * diameter    # = -0.6 * base_radius

    # Arc radius: distance from center to opposite base corner
    arc_r = math.sqrt((cx_right - (-base_radius))**2)  # = 1.6 * base_radius

    if t <= 0.5:
        # Left half: arc centered at cx_right (right center draws left side)
        # Angle from base to apex
        base_angle = math.acos((base_radius - cx_right) / arc_r)  # angle at right base
        apex_angle = math.acos((0 - cx_right) / arc_r)  # angle at apex (x=0)
        angle = base_angle + (apex_angle - base_angle) * (t / 0.5)
        # Wait — we need to think about this more carefully.
        # The right center is at (cx_right, 0) = (0.6R, 0).
        # The left base corner is at (-R, 0). The arc from left base to apex.
        # Actually, the LEFT side of the dome is drawn by the arc centered on the RIGHT.
        # Angle from cx_right to (-R, 0): cos(a) = (-R - cx_right) / arc_r = -1.6R / 1.6R = -1, a = pi
        # Angle from cx_right to (0, apex_y): cos(a) = (0 - 0.6R) / 1.6R = -0.375, a = acos(-0.375)
        angle_base = math.pi  # angle to left base corner
        angle_apex = math.acos(-cx_right / arc_r)  # angle to apex
        angle = angle_base + (angle_apex - angle_base) * (t / 0.5)
        x = cx_right + arc_r * math.cos(angle)
        y = arc_r * math.sin(angle)
    else:
        # Right half: arc centered at cx_left (left center draws right side)
        angle_apex = math.pi - math.acos(-cx_left / arc_r)
        angle_base = 0.0  # angle to right base corner
        # From apex to right base
        frac = (t - 0.5) / 0.5
        angle = angle_apex + (angle_base - angle_apex) * frac
        x = cx_left + arc_r * math.cos(angle)
        y = arc_r * math.sin(angle)

    return (x, y)


def dome_profile_at_height(y: float, base_radius: float) -> tuple[float, float]:
    """Return (x_left, x_right) where the dome profile crosses height y.

    Uses the same pointed-fifth geometry. Returns the x-coordinates of the
    outer shell at the given height.
    """
    cx_right = 0.6 * base_radius
    cx_left = -0.6 * base_radius
    arc_r = 1.6 * base_radius

    # Left side (arc centered at cx_right):
    # (x - cx_right)^2 + y^2 = arc_r^2, x < 0
    discriminant = arc_r**2 - y**2
    if discriminant < 0:
        return (0.0, 0.0)  # above the dome
    # x = cx_right + cos(angle) * arc_r where sin(angle) = y / arc_r
    sin_a = y / arc_r
    cos_a = math.sqrt(1 - sin_a**2)
    x_left = cx_right - cos_a * arc_r   # negative x solution
    x_right = cx_left + cos_a * arc_r   # positive x solution (symmetric)

    return (x_left, x_right)


def octagon_points(radius: float) -> list[tuple[float, float]]:
    """Return 8 vertices of a regular octagon inscribed in a circle of given radius.

    First vertex is at the top (12 o'clock), proceeding clockwise.
    """
    points = []
    for i in range(8):
        angle = math.pi / 2 + i * (2 * math.pi / 8)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    return points
```

**Note:** The dome_profile function involves non-trivial trigonometry. The implementation above is a starting point — run the tests and iterate until the geometry is correct. The key constraints are:
- Endpoints at (±base_radius, 0)
- Symmetric about x=0
- Apex height > base_radius (pointed, not semicircular)
- Smooth curve (no discontinuity at t=0.5)

- [ ] **Step 4: Run tests and iterate until they pass**

```bash
python -m pytest tests/test_geometry.py -v
```

Expected: all 6 tests pass. If any fail, debug the trigonometry — the arc center placement and angle calculations are the tricky part.

- [ ] **Step 5: Visual sanity check**

Write a quick one-off script to verify the dome profile looks right:

```bash
python -c "
import geometry
pts = [geometry.dome_profile(t/100, 100) for t in range(101)]
for x, y in pts[::10]:
    print(f'  ({x:7.1f}, {y:7.1f})')
print(f'Apex height: {max(y for _, y in pts):.1f} (should be > 100)')
"
```

Verify apex height is roughly 130-140 (for a pointed-fifth arch with base_radius=100).

- [ ] **Step 6: Commit**

```bash
git add geometry.py tests/test_geometry.py
git commit -m "feat: add geometry module with pointed-fifth dome profile and octagon math"
```

---

## Chunk 2: Renderer — Construction Frame Drawing

### Task 4: Canvas scaffolding and title/annotation bars

**Files:**
- Create: `renderer.py`
- Create: `tests/test_renderer.py`

- [ ] **Step 1: Write test for canvas creation and frame layout**

```python
# tests/test_renderer.py
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
    renderer.draw_title_bar(ctx, "BUILDING BRUNELLESCHI'S DOME · 1420–1436")
    # If we get here without error, the function works


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_renderer.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'renderer'`

- [ ] **Step 3: Implement renderer.py with canvas, title bar, annotation bar, and background**

```python
# renderer.py
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

# Phase annotations — text shown in the bottom bar for each phase
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
    # Gold border line below title
    ctx.set_line_width(1)
    ctx.move_to(40, 40)
    ctx.line_to(WIDTH - 40, 40)
    ctx.stroke()


def draw_annotation_bar(ctx: cairo.Context, text: str):
    """Draw the bottom annotation bar with gold border and explanation text."""
    bar_y = HEIGHT - 50
    bar_height = 30
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(11)
    extents = ctx.text_extents(text)
    bar_width = extents.width + 32
    bar_x = (WIDTH - bar_width) / 2

    # Background box
    palette.set_color(ctx, palette.ANNOTATION_BG)
    ctx.rectangle(bar_x, bar_y, bar_width, bar_height)
    ctx.fill()

    # Gold border
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(1)
    ctx.rectangle(bar_x, bar_y, bar_width, bar_height)
    ctx.stroke()

    # Text
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
    # Dashed center line
    ctx.set_dash([6, 4])
    ctx.set_line_width(1)
    ctx.move_to(WIDTH // 2, 45)
    ctx.line_to(WIDTH // 2, HEIGHT - 60)
    ctx.stroke()
    ctx.set_dash([])  # reset


def draw_drum(ctx: cairo.Context, progress: float):
    """Draw the octagonal drum/base that the dome sits on.

    progress: 0.0-1.0, controls how much of the drum is visible (rising animation).
    """
    drum_height = 60
    visible_height = drum_height * progress
    if visible_height <= 0:
        return

    # Drum rectangle (simplified as rectangle for 2D front view)
    drum_top = DOME_BASE_Y - visible_height
    drum_width = DOME_BASE_RADIUS * 2 + 40  # slightly wider than dome base

    # Cream/stone colored drum
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2, drum_top, drum_width, visible_height)
    ctx.fill()

    # Darker stone border
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(2)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2, drum_top, drum_width, visible_height)
    ctx.stroke()

    # Cathedral walls below (always fully visible once drum starts)
    wall_height = 80
    wall_top = DOME_BASE_Y
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2 - 20, wall_top, drum_width + 40, wall_height)
    ctx.fill()
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(2)
    ctx.rectangle(DOME_CENTER_X - drum_width // 2 - 20, wall_top, drum_width + 40, wall_height)
    ctx.stroke()


def draw_dome_exterior(ctx: cairo.Context, height_frac: float):
    """Draw the exterior (left half) of the dome up to height_frac of total height.

    height_frac: 0.0-1.0, fraction of dome height completed.
    """
    if height_frac <= 0:
        return

    # Get dome apex to know total height
    _, apex_y = geometry.dome_profile(0.5, DOME_BASE_RADIUS)
    max_height = apex_y
    current_height = max_height * height_frac

    # Build the dome outline from base to current height (left half only)
    points = []
    num_steps = 50
    for i in range(num_steps + 1):
        t = i / num_steps * 0.5  # left half only: t in [0, 0.5]
        x, y = geometry.dome_profile(t, DOME_BASE_RADIUS)
        if y > current_height:
            # Interpolate to find exact cutoff point
            if i > 0:
                t_prev = (i - 1) / num_steps * 0.5
                x_prev, y_prev = geometry.dome_profile(t_prev, DOME_BASE_RADIUS)
                frac = (current_height - y_prev) / (y - y_prev) if y != y_prev else 0
                x_cut = x_prev + frac * (x - x_prev)
                points.append((x_cut, current_height))
            break
        points.append((x, y))

    if len(points) < 2:
        return

    # Also add the center line point at current height (to close the shape at x=0)
    # and base closing points
    # Convert to screen coordinates: x is centered, y is inverted
    screen_points = [
        (DOME_CENTER_X + px, DOME_BASE_Y - py) for px, py in points
    ]
    # Close: go straight down at center line, then along base back to start
    screen_points.append((DOME_CENTER_X, DOME_BASE_Y - current_height))
    screen_points.append((DOME_CENTER_X, DOME_BASE_Y))
    screen_points.append(screen_points[0])

    # Clip to left half
    ctx.save()
    ctx.rectangle(0, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    # Fill with terracotta gradient
    ctx.move_to(*screen_points[0])
    for px, py in screen_points[1:]:
        ctx.line_to(px, py)
    ctx.close_path()

    # Gradient from terracotta at base to lighter at top
    grad = cairo.LinearGradient(DOME_CENTER_X, DOME_BASE_Y, DOME_CENTER_X, DOME_BASE_Y - max_height)
    grad.add_color_stop_rgb(0.0, *palette.DARK_BROWN)
    grad.add_color_stop_rgb(0.5, *palette.SIENNA)
    grad.add_color_stop_rgb(1.0, *palette.TERRACOTTA)
    ctx.set_source(grad)
    ctx.fill_preserve()

    # Outline
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(2)
    ctx.stroke()

    # Draw horizontal course lines for brick texture
    course_spacing = 8
    for cy in range(0, int(current_height), course_spacing):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        screen_y = DOME_BASE_Y - cy
        palette.set_color(ctx, palette.RIB_DARK)
        ctx.set_line_width(0.5)
        ctx.move_to(DOME_CENTER_X + x_left, screen_y)
        ctx.line_to(DOME_CENTER_X, screen_y)  # only to center (left half)
        ctx.stroke()

    ctx.restore()


def draw_dome_cutaway(ctx: cairo.Context, height_frac: float, show_ribs: bool = False,
                       show_chains: bool = False, show_herringbone: bool = False):
    """Draw the cutaway (right half) showing inner/outer shells, ribs, chains.

    height_frac: 0.0-1.0, fraction of dome height completed.
    show_ribs: whether to draw the structural ribs.
    show_chains: whether to draw the chain rings.
    show_herringbone: whether to show herringbone brick pattern.
    """
    if height_frac <= 0:
        return

    _, apex_y = geometry.dome_profile(0.5, DOME_BASE_RADIUS)
    max_height = apex_y
    current_height = max_height * height_frac

    # Shell thickness parameters (proportional to dome radius)
    outer_thickness = DOME_BASE_RADIUS * 0.12
    inner_thickness = DOME_BASE_RADIUS * 0.15
    gap = DOME_BASE_RADIUS * 0.08

    ctx.save()
    ctx.rectangle(WIDTH // 2, 0, WIDTH // 2, HEIGHT)
    ctx.clip()

    # Draw outer shell (right edge of dome)
    for cy in range(0, int(current_height), 2):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy
        # Outer shell: from x_right - outer_thickness to x_right
        outer_left = DOME_CENTER_X + x_right - outer_thickness
        outer_right = DOME_CENTER_X + x_right
        palette.set_color(ctx, palette.SIENNA)
        ctx.rectangle(outer_left, screen_y, outer_right - outer_left, 2)
        ctx.fill()

    # Draw inner shell
    for cy in range(0, int(current_height), 2):
        x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
        if x_right <= 0:
            continue
        screen_y = DOME_BASE_Y - cy
        inner_right = DOME_CENTER_X + x_right - outer_thickness - gap
        inner_left = inner_right - inner_thickness
        palette.set_color(ctx, palette.TERRACOTTA)
        ctx.rectangle(max(DOME_CENTER_X, inner_left), screen_y, inner_right - max(DOME_CENTER_X, inner_left), 2)
        ctx.fill()

    # Herringbone pattern on the inner face of the outer shell
    if show_herringbone:
        brick_h = 6
        brick_w = 12
        for cy in range(0, int(current_height), brick_h):
            x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            if x_right <= 0:
                continue
            screen_y = DOME_BASE_Y - cy
            shell_left = DOME_CENTER_X + x_right - outer_thickness
            shell_right = DOME_CENTER_X + x_right
            row = cy // brick_h
            # Every 4th brick is vertical (herringbone spine)
            for bx in range(int(shell_left), int(shell_right), brick_w):
                if (row + bx // brick_w) % 4 == 0:
                    # Vertical brick
                    palette.set_color(ctx, palette.DARK_BROWN)
                    ctx.rectangle(bx, screen_y - brick_h, brick_w // 3, brick_h)
                    ctx.fill()

    # Chain rings
    if show_chains:
        chain_interval = max_height / 5
        palette.set_color(ctx, palette.GOLD)
        ctx.set_line_width(3)
        for i in range(1, 5):
            cy = chain_interval * i
            if cy > current_height:
                break
            x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
            screen_y = DOME_BASE_Y - cy
            ctx.move_to(DOME_CENTER_X, screen_y)
            ctx.line_to(DOME_CENTER_X + x_right, screen_y)
            ctx.stroke()

    # Ribs (major ribs as thick lines)
    if show_ribs:
        palette.set_color(ctx, palette.RIB_DARK)
        ctx.set_line_width(4)
        # Draw 2 visible major ribs on the right half (at ~22.5° and ~67.5° from center)
        for rib_frac in [0.15, 0.35]:
            points = []
            for cy in range(0, int(current_height), 4):
                x_left, x_right = geometry.dome_profile_at_height(cy, DOME_BASE_RADIUS)
                rib_x = DOME_CENTER_X + x_right * rib_frac
                points.append((rib_x, DOME_BASE_Y - cy))
            if len(points) >= 2:
                ctx.move_to(*points[0])
                for p in points[1:]:
                    ctx.line_to(*p)
                ctx.stroke()

    ctx.restore()


def draw_lantern(ctx: cairo.Context):
    """Draw the lantern atop the completed dome."""
    _, apex_y = geometry.dome_profile(0.5, DOME_BASE_RADIUS)
    lantern_base_y = DOME_BASE_Y - apex_y
    lantern_width = 30
    lantern_height = 50

    # Lantern base ring
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - lantern_width, lantern_base_y - 8, lantern_width * 2, 8)
    ctx.fill()

    # Lantern body
    palette.set_color(ctx, palette.CREAM)
    ctx.rectangle(DOME_CENTER_X - lantern_width * 0.6, lantern_base_y - 8 - lantern_height,
                  lantern_width * 1.2, lantern_height)
    ctx.fill()

    # Lantern cap (small cone)
    palette.set_color(ctx, palette.DARK_BROWN)
    ctx.move_to(DOME_CENTER_X - lantern_width * 0.6, lantern_base_y - 8 - lantern_height)
    ctx.line_to(DOME_CENTER_X, lantern_base_y - 8 - lantern_height - 25)
    ctx.line_to(DOME_CENTER_X + lantern_width * 0.6, lantern_base_y - 8 - lantern_height)
    ctx.close_path()
    ctx.fill()

    # Outline
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1.5)
    ctx.rectangle(DOME_CENTER_X - lantern_width, lantern_base_y - 8, lantern_width * 2, 8)
    ctx.stroke()
    ctx.rectangle(DOME_CENTER_X - lantern_width * 0.6, lantern_base_y - 8 - lantern_height,
                  lantern_width * 1.2, lantern_height)
    ctx.stroke()


def render_construction_frame(progress: float, phase: int) -> cairo.ImageSurface:
    """Render a single construction frame.

    progress: 0.0-1.0, overall construction progress within this phase.
    phase: the current phase number (2, 4, 6, 8, 10, 11, 12).

    Returns the rendered Cairo surface.
    """
    surface = create_surface()
    ctx = cairo.Context(surface)

    draw_background(ctx)
    draw_title_bar(ctx, "BUILDING BRUNELLESCHI'S DOME · 1420–1436")
    draw_split_labels(ctx)

    # Drum is always fully visible once we're past phase 2
    drum_progress = min(1.0, progress) if phase == 2 else 1.0
    draw_drum(ctx, drum_progress)

    # Dome height depends on phase
    if phase == 2:
        dome_frac = 0.0  # drum only
    elif phase == 4:
        dome_frac = progress * 0.15  # shells just starting
    elif phase == 6:
        dome_frac = 0.15 + progress * 0.35  # up to 50%
    elif phase == 8:
        dome_frac = 0.50 + progress * 0.15  # up to 65%
    elif phase == 10:
        dome_frac = 0.65 + progress * 0.30  # up to 95%
    elif phase >= 11:
        dome_frac = 0.95 + progress * 0.05  # final 5%
    else:
        dome_frac = 0.0

    draw_dome_exterior(ctx, dome_frac)
    draw_dome_cutaway(
        ctx, dome_frac,
        show_ribs=(phase >= 8),
        show_chains=(phase >= 8),
        show_herringbone=(phase >= 6),
    )

    if phase >= 11 and progress >= 0.5:
        draw_lantern(ctx)

    # Annotation
    annotation = PHASE_ANNOTATIONS.get(phase, "")
    if annotation:
        draw_annotation_bar(ctx, annotation)

    return surface
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_renderer.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 5: Visual sanity check — render a test frame to PNG**

```bash
python -c "
import renderer
surface = renderer.render_construction_frame(progress=0.5, phase=6)
surface.write_to_png('frames/test_phase6.png')
print('Wrote frames/test_phase6.png')
"
```

Open `frames/test_phase6.png` and verify: dark background, title bar, dome partially built with exterior on left and cutaway on right, annotation bar at bottom. The geometry doesn't need to be perfect yet — this is a sanity check.

- [ ] **Step 6: Commit**

```bash
git add renderer.py tests/test_renderer.py
git commit -m "feat: add renderer module with construction frame drawing"
```

---

## Chunk 3: Insets and GIF Assembly

### Task 5: Inset detail frame renderers

**Files:**
- Create: `insets.py`
- Create: `tests/test_insets.py`

- [ ] **Step 1: Write tests for inset renderers**

```python
# tests/test_insets.py
import cairo
import insets

def _make_ctx():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    return cairo.Context(surface), surface

def test_render_arch_comparison():
    """Should render without error and return a surface."""
    surface = insets.render_arch_comparison()
    assert surface.get_width() == 800
    assert surface.get_height() == 600

def test_render_herringbone():
    surface = insets.render_herringbone()
    assert surface.get_width() == 800

def test_render_chain_rings():
    surface = insets.render_chain_rings()
    assert surface.get_width() == 800

def test_render_ox_hoist():
    surface = insets.render_ox_hoist()
    assert surface.get_width() == 800
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_insets.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement insets.py**

Each inset function creates a fresh 800×600 surface, draws the background, "DETAIL: ..." header, the diagram, explanation text, and "returning to construction..." footer.

```python
# insets.py
"""Detail inset frame renderers for Brunelleschi's dome animation.

Each function renders a single teaching inset frame explaining one
engineering innovation. All insets share the same warm palette and
layout template: DETAIL header, diagram area, explanation text box,
footer.
"""
import math
import cairo
import palette
import renderer  # reuse create_surface, draw_background, WIDTH, HEIGHT


def _draw_inset_template(ctx: cairo.Context, title: str, explanation: str):
    """Draw the shared inset frame template: background, header, explanation box, footer."""
    renderer.draw_background(ctx)

    # Header: "DETAIL: <TITLE>"
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(14)
    palette.set_color(ctx, palette.GOLD)
    header_text = f"DETAIL: {title}"
    extents = ctx.text_extents(header_text)
    ctx.move_to((renderer.WIDTH - extents.width) / 2, 28)
    ctx.show_text(header_text)
    # Border
    ctx.set_line_width(1)
    ctx.move_to(40, 40)
    ctx.line_to(renderer.WIDTH - 40, 40)
    ctx.stroke()

    # Explanation text box (bottom third)
    box_x, box_y = 60, 430
    box_w, box_h = renderer.WIDTH - 120, 110
    palette.set_color(ctx, palette.ANNOTATION_BG)
    ctx.rectangle(box_x, box_y, box_w, box_h)
    ctx.fill()
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(1)
    ctx.rectangle(box_x, box_y, box_w, box_h)
    ctx.stroke()

    # Wrap and draw explanation text
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(12)
    palette.set_color(ctx, palette.TEXT)
    _draw_wrapped_text(ctx, explanation, box_x + 16, box_y + 24, box_w - 32, line_height=18)

    # Footer
    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    footer = "▸ returning to construction..."
    extents = ctx.text_extents(footer)
    ctx.move_to((renderer.WIDTH - extents.width) / 2, renderer.HEIGHT - 12)
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
    _draw_inset_template(ctx, "POINTED-FIFTH ARCH",
        "A semicircular dome pushes outward at the base, requiring heavy scaffolding "
        "(centering) to hold it up during construction. Brunelleschi's pointed-fifth "
        "arch redirects forces more vertically, making each ring of bricks stable on "
        "its own. The center of each arc is placed at 4/5 of the base diameter from "
        "the opposite side, producing the distinctive pointed profile.")

    diagram_y = 80
    diagram_h = 320
    mid_x = renderer.WIDTH // 2

    # Left: semicircular arch
    center_x_left = mid_x // 2
    arch_radius = 100
    base_y = diagram_y + diagram_h - 40

    # Semicircle
    palette.set_color(ctx, palette.SIENNA)
    ctx.set_line_width(3)
    ctx.arc(center_x_left, base_y, arch_radius, math.pi, 0)
    ctx.stroke()

    # Base line
    ctx.set_line_width(2)
    ctx.move_to(center_x_left - arch_radius, base_y)
    ctx.line_to(center_x_left + arch_radius, base_y)
    ctx.stroke()

    # Outward thrust arrows
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    for dx in [-1, 1]:
        ax = center_x_left + dx * arch_radius
        ctx.move_to(ax, base_y)
        ctx.line_to(ax + dx * 30, base_y)
        # Arrowhead
        ctx.line_to(ax + dx * 25, base_y - 5)
        ctx.move_to(ax + dx * 30, base_y)
        ctx.line_to(ax + dx * 25, base_y + 5)
        ctx.stroke()

    # Label
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(11)
    label = "Semicircular"
    ext = ctx.text_extents(label)
    ctx.move_to(center_x_left - ext.width / 2, base_y + 25)
    ctx.show_text(label)
    label2 = "Needs scaffolding"
    ext2 = ctx.text_extents(label2)
    ctx.move_to(center_x_left - ext2.width / 2, base_y + 40)
    ctx.show_text(label2)

    # Right: pointed-fifth arch
    center_x_right = mid_x + mid_x // 2
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.set_line_width(3)

    # Draw pointed arch using dome_profile
    import geometry
    points = []
    for i in range(51):
        t = i / 50.0
        x, y = geometry.dome_profile(t, arch_radius)
        points.append((center_x_right + x, base_y - y))

    ctx.move_to(*points[0])
    for p in points[1:]:
        ctx.line_to(*p)
    ctx.stroke()

    # Base line
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.set_line_width(2)
    ctx.move_to(center_x_right - arch_radius, base_y)
    ctx.line_to(center_x_right + arch_radius, base_y)
    ctx.stroke()

    # Downward thrust arrows (more vertical)
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    for dx in [-1, 1]:
        ax = center_x_right + dx * arch_radius
        ctx.move_to(ax, base_y)
        ctx.line_to(ax + dx * 10, base_y + 30)
        ctx.line_to(ax + dx * 5, base_y + 25)
        ctx.move_to(ax + dx * 10, base_y + 30)
        ctx.line_to(ax + dx * 15, base_y + 25)
        ctx.stroke()

    # Label
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(11)
    label = "Pointed-Fifth"
    ext = ctx.text_extents(label)
    ctx.move_to(center_x_right - ext.width / 2, base_y + 25)
    ctx.show_text(label)
    label2 = "Self-supporting"
    ext2 = ctx.text_extents(label2)
    ctx.move_to(center_x_right - ext2.width / 2, base_y + 40)
    ctx.show_text(label2)

    # "VS" in center
    palette.set_color(ctx, palette.GOLD)
    ctx.set_font_size(16)
    ctx.move_to(mid_x - 10, base_y - arch_radius // 2)
    ctx.show_text("vs")

    return surface


def render_herringbone() -> cairo.ImageSurface:
    """Inset 2: Herringbone brickwork close-up."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "HERRINGBONE BRICKWORK",
        "Bricks are laid mostly horizontal, but with vertical bricks inserted at "
        "regular intervals. These vertical 'spine' bricks act as teeth that lock "
        "each horizontal course in place, preventing wet mortar from sliding before "
        "it sets. This technique — borrowed from ancient Roman construction — allowed "
        "Brunelleschi to build without centering (temporary wooden scaffolding from below).")

    # Draw a zoomed brick pattern
    start_x, start_y = 150, 80
    brick_w, brick_h = 48, 16
    rows = 18
    cols = 10

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * brick_w + (row % 2) * (brick_w // 2)
            y = start_y + row * brick_h

            if y > 400:
                continue

            is_vertical = (col % 4 == 2)  # every 4th column is a vertical brick

            if is_vertical:
                # Vertical brick — spans 2 rows
                palette.set_color(ctx, palette.DARK_BROWN)
                ctx.rectangle(x + brick_w * 0.3, y, brick_w * 0.4, brick_h * 2)
                ctx.fill()
                palette.set_color(ctx, palette.RIB_DARK)
                ctx.set_line_width(0.5)
                ctx.rectangle(x + brick_w * 0.3, y, brick_w * 0.4, brick_h * 2)
                ctx.stroke()
            else:
                # Horizontal brick
                palette.set_color(ctx, palette.TERRACOTTA if (row + col) % 3 != 0 else palette.SIENNA)
                ctx.rectangle(x, y, brick_w - 2, brick_h - 2)
                ctx.fill()
                palette.set_color(ctx, palette.RIB_DARK)
                ctx.set_line_width(0.5)
                ctx.rectangle(x, y, brick_w - 2, brick_h - 2)
                ctx.stroke()

    # Arrow annotations pointing to vertical bricks
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    arrow_x = start_x + 2 * brick_w + brick_w * 0.5
    ctx.move_to(arrow_x, 75)
    ctx.line_to(arrow_x, 85)
    ctx.stroke()

    ctx.set_font_size(10)
    palette.set_color(ctx, palette.GOLD)
    ctx.move_to(start_x, 415)
    ctx.show_text("↑ vertical 'spine' bricks lock horizontal courses in place ↑")

    return surface


def render_chain_rings() -> cairo.ImageSurface:
    """Inset 3: Chain rings cross-section."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "CHAIN RINGS",
        "At regular intervals, Brunelleschi embedded horizontal tension rings made of "
        "sandstone blocks linked with iron clamps, reinforced with wooden tie-beams. "
        "These act like the hoops on a barrel — resisting the outward thrust that would "
        "otherwise push the dome apart. There are four major stone-and-iron chains plus "
        "additional wooden chains between them.")

    # Cross-section view: a radial slice through the dome wall
    cx = renderer.WIDTH // 2
    base_y = 380
    section_width = 400
    section_height = 300

    # Outer shell
    outer_left = cx - section_width // 2
    outer_w = 40
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(outer_left, base_y - section_height, outer_w, section_height)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(outer_left, base_y - section_height, outer_w, section_height)
    ctx.stroke()

    # Inner shell
    inner_left = outer_left + outer_w + 60  # gap of 60px
    inner_w = 50
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.rectangle(inner_left, base_y - section_height, inner_w, section_height)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.rectangle(inner_left, base_y - section_height, inner_w, section_height)
    ctx.stroke()

    # Gap label
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(10)
    ctx.move_to(outer_left + outer_w + 15, base_y - section_height // 2)
    ctx.show_text("gap")

    # Corresponding right side (mirror)
    outer_right_x = cx + section_width // 2 - outer_w
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(outer_right_x, base_y - section_height, outer_w, section_height)
    ctx.fill()

    inner_right_x = outer_right_x - 60 - inner_w
    palette.set_color(ctx, palette.TERRACOTTA)
    ctx.rectangle(inner_right_x, base_y - section_height, inner_w, section_height)
    ctx.fill()

    # Chain rings (horizontal bands across the gap)
    chain_positions = [0.25, 0.45, 0.65, 0.85]
    for frac in chain_positions:
        chain_y = base_y - section_height * frac
        # Stone blocks
        palette.set_color(ctx, palette.CREAM)
        ctx.rectangle(outer_left - 5, chain_y - 8, section_width + 10, 16)
        ctx.fill()
        # Iron clamp marks
        palette.set_color(ctx, palette.GOLD)
        ctx.set_line_width(2)
        ctx.rectangle(outer_left - 5, chain_y - 8, section_width + 10, 16)
        ctx.stroke()
        # Label first one
        if frac == chain_positions[0]:
            palette.set_color(ctx, palette.GOLD)
            ctx.set_font_size(10)
            ctx.move_to(cx + section_width // 2 + 15, chain_y + 4)
            ctx.show_text("← stone + iron chain")

    # Labels for shells
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(10)
    ctx.move_to(outer_left, base_y + 15)
    ctx.show_text("outer shell")
    ctx.move_to(inner_left, base_y + 15)
    ctx.show_text("inner shell")

    return surface


def render_ox_hoist() -> cairo.ImageSurface:
    """Inset 4: Brunelleschi's ox-hoist crane."""
    surface = renderer.create_surface()
    ctx = cairo.Context(surface)
    _draw_inset_template(ctx, "OX-HOIST CRANE",
        "Brunelleschi invented a reversible hoist powered by oxen walking in a circle. "
        "A clever gear mechanism allowed the load direction to reverse without "
        "unhitching and turning the oxen around — the first known reversible gear. "
        "This crane lifted over 70 million pounds of material to the top of the dome, "
        "an engineering marvel that amazed contemporaries.")

    cx = renderer.WIDTH // 2
    base_y = 390

    # Central vertical shaft
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(cx - 8, base_y - 280, 16, 280)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1.5)
    ctx.rectangle(cx - 8, base_y - 280, 16, 280)
    ctx.stroke()

    # Horizontal arm at top
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(cx - 80, base_y - 280, 160, 12)
    ctx.fill()
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.rectangle(cx - 80, base_y - 280, 160, 12)
    ctx.stroke()

    # Rope from arm end going down
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.move_to(cx + 75, base_y - 274)
    ctx.line_to(cx + 75, base_y - 180)
    ctx.stroke()
    # Weight/load box
    palette.set_color(ctx, palette.SIENNA)
    ctx.rectangle(cx + 60, base_y - 180, 30, 25)
    ctx.fill()
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(9)
    ctx.move_to(cx + 63, base_y - 163)
    ctx.show_text("load")

    # Gear mechanism (circle at shaft base)
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(2)
    ctx.arc(cx, base_y - 40, 25, 0, 2 * math.pi)
    ctx.stroke()
    # Gear teeth suggestion
    for i in range(8):
        angle = i * math.pi / 4
        x1 = cx + 25 * math.cos(angle)
        y1 = (base_y - 40) + 25 * math.sin(angle)
        x2 = cx + 32 * math.cos(angle)
        y2 = (base_y - 40) + 32 * math.sin(angle)
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    # Label: "reversible gear"
    palette.set_color(ctx, palette.GOLD)
    ctx.set_font_size(10)
    ctx.move_to(cx + 40, base_y - 35)
    ctx.show_text("← reversible gear")

    # Ox walking circle at base
    palette.set_color(ctx, palette.RIB_DARK)
    ctx.set_line_width(1)
    ctx.set_dash([4, 3])
    ctx.arc(cx, base_y, 80, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_dash([])

    # Ox (simplified)
    ox_x = cx + 70
    ox_y = base_y + 10
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.rectangle(ox_x - 15, ox_y - 12, 30, 18)
    ctx.fill()
    palette.set_color(ctx, palette.TEXT)
    ctx.set_font_size(9)
    ctx.move_to(ox_x - 8, ox_y + 2)
    ctx.show_text("ox")

    # Horizontal beam from ox to shaft
    palette.set_color(ctx, palette.DRUM_STONE)
    ctx.set_line_width(3)
    ctx.move_to(cx, base_y)
    ctx.line_to(ox_x - 15, ox_y)
    ctx.stroke()

    # Walking direction arrow
    palette.set_color(ctx, palette.GOLD)
    ctx.set_line_width(1.5)
    ctx.arc(cx, base_y, 90, -0.3, 0.5)
    ctx.stroke()
    # Arrowhead
    end_x = cx + 90 * math.cos(0.5)
    end_y = base_y + 90 * math.sin(0.5)
    ctx.move_to(end_x, end_y)
    ctx.line_to(end_x - 8, end_y - 5)
    ctx.move_to(end_x, end_y)
    ctx.line_to(end_x + 2, end_y - 8)
    ctx.stroke()

    return surface
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_insets.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 5: Visual sanity check — render each inset to PNG**

```bash
python -c "
import insets
for name, fn in [('arch', insets.render_arch_comparison), ('herringbone', insets.render_herringbone),
                  ('chains', insets.render_chain_rings), ('oxhoist', insets.render_ox_hoist)]:
    surface = fn()
    surface.write_to_png(f'frames/test_inset_{name}.png')
    print(f'Wrote frames/test_inset_{name}.png')
"
```

Open each PNG and verify it looks reasonable: correct palette, readable annotations, diagram content visible.

- [ ] **Step 6: Commit**

```bash
git add insets.py tests/test_insets.py
git commit -m "feat: add four detail inset frame renderers"
```

---

### Task 6: Main orchestrator and GIF assembly

**Files:**
- Create: `dome.py`
- Create: `tests/test_dome.py`

- [ ] **Step 1: Write test for frame sequence definition**

```python
# tests/test_dome.py
import dome


def test_frame_sequence_defined():
    """FRAME_SEQUENCE should be a list of (phase, frame_count, delay_ms) tuples."""
    assert len(dome.FRAME_SEQUENCE) > 0
    total_frames = sum(count for _, count, _ in dome.FRAME_SEQUENCE)
    assert 60 <= total_frames <= 100, f"Total frames {total_frames} outside expected range"


def test_generate_frames_returns_list():
    """generate_frames should return a list of (surface, delay_ms) tuples."""
    # Generate just the first 2 entries to keep test fast
    frames = dome.generate_frames(limit=2)
    assert len(frames) >= 1
    surface, delay = frames[0]
    assert surface.get_width() == 800
    assert delay > 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_dome.py -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement dome.py**

```python
# dome.py
"""Main entry point for Brunelleschi's dome GIF generation.

Orchestrates frame generation across construction phases and inset details,
then assembles everything into an animated GIF.
"""
import os
import cairo
import imageio.v3 as iio
import numpy as np

import renderer
import insets

# Frame sequence: (phase, frame_count, delay_ms)
# Phases with negative numbers are insets:
#   -1 = arch comparison, -2 = herringbone, -3 = chain rings, -4 = ox-hoist
FRAME_SEQUENCE = [
    (1, 1, 2000),       # Title card
    (2, 8, 200),        # Base octagon & drum
    (-1, 3, 1500),      # Inset: pointed-fifth arch
    (4, 6, 200),        # Inner & outer shells begin
    (-2, 3, 1500),      # Inset: herringbone
    (6, 15, 200),       # Herringbone courses rise
    (-3, 3, 1500),      # Inset: chain rings
    (8, 8, 200),        # Chain rings + ribs
    (-4, 3, 1500),      # Inset: ox-hoist
    (10, 15, 200),      # Progressive ring closure
    (11, 6, 200),       # Lantern & oculus
    (12, 1, 3000),      # Final reveal
]

# Inset renderers keyed by phase number
INSET_RENDERERS = {
    -1: insets.render_arch_comparison,
    -2: insets.render_herringbone,
    -3: insets.render_chain_rings,
    -4: insets.render_ox_hoist,
}


def _surface_to_numpy(surface: cairo.ImageSurface) -> np.ndarray:
    """Convert a Cairo ARGB32 surface to a numpy RGB array for imageio."""
    buf = surface.get_data()
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(surface.get_height(), surface.get_width(), 4)
    # Cairo uses BGRA byte order on little-endian, convert to RGB
    rgb = np.empty((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    rgb[:, :, 0] = arr[:, :, 2]  # R
    rgb[:, :, 1] = arr[:, :, 1]  # G
    rgb[:, :, 2] = arr[:, :, 0]  # B
    return rgb


def generate_frames(limit: int = None) -> list[tuple[cairo.ImageSurface, int]]:
    """Generate all frames as (surface, delay_ms) tuples.

    limit: if set, only process the first `limit` entries in FRAME_SEQUENCE.
    """
    frames = []
    sequence = FRAME_SEQUENCE[:limit] if limit else FRAME_SEQUENCE

    for phase, count, delay in sequence:
        if phase < 0:
            # Inset frame — render once, repeat `count` times
            render_fn = INSET_RENDERERS[phase]
            surface = render_fn()
            for _ in range(count):
                frames.append((surface, delay))
        elif phase == 1:
            # Title card — use phase 2 at progress 0 (just background + title)
            surface = renderer.render_construction_frame(progress=0.0, phase=2)
            frames.append((surface, delay))
        elif phase == 12:
            # Final reveal — fully built dome
            surface = renderer.render_construction_frame(progress=1.0, phase=12)
            frames.append((surface, delay))
        else:
            # Construction phase — render `count` frames with progress 0..1
            for i in range(count):
                progress = i / max(count - 1, 1)
                surface = renderer.render_construction_frame(progress=progress, phase=phase)
                frames.append((surface, delay))

    return frames


def assemble_gif(frames: list[tuple[cairo.ImageSurface, int]], output_path: str):
    """Assemble frames into an animated GIF."""
    images = []
    durations = []

    for surface, delay_ms in frames:
        rgb = _surface_to_numpy(surface)
        images.append(rgb)
        durations.append(delay_ms / 1000.0)  # imageio expects seconds

    # imageio v3 API
    iio.imwrite(
        output_path,
        images,
        extension=".gif",
        loop=0,  # infinite loop
        duration=durations,
    )


def main():
    """Generate all frames and assemble the GIF."""
    os.makedirs("frames", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    print("Generating frames...")
    frames = generate_frames()
    print(f"Generated {len(frames)} frames")

    # Save individual PNGs for debugging
    for i, (surface, delay) in enumerate(frames):
        surface.write_to_png(f"frames/frame_{i:03d}.png")

    # Assemble GIF
    output_path = "output/brunelleschi_dome.gif"
    print(f"Assembling GIF: {output_path}")
    assemble_gif(frames, output_path)

    # Report file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Done! {output_path} ({size_mb:.1f} MB)")
    if size_mb > 15:
        print("WARNING: File > 15MB. Consider: gifsicle -O3 --lossy=80 -o optimized.gif brunelleschi_dome.gif")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_dome.py -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add dome.py tests/test_dome.py
git commit -m "feat: add dome orchestrator with frame sequence and GIF assembly"
```

---

### Task 7: End-to-end generation and visual polish

**Files:**
- Modify: all files as needed for visual adjustments

- [ ] **Step 1: Run full generation**

```bash
cd /Users/dannyswift/Projects/uncharted_territories && python dome.py
```

Expected: `output/brunelleschi_dome.gif` created successfully with file size reported.

- [ ] **Step 2: Review the GIF**

Open `output/brunelleschi_dome.gif` in a browser or image viewer. Check:
- Title card displays correctly
- Drum/base rises smoothly
- Arch comparison inset is clear and readable
- Dome shells rise with visible cutaway on right side
- Herringbone inset shows clear brick pattern
- Construction continues with herringbone visible in cutaway
- Chain rings inset shows cross-section clearly
- Ribs and chain rings appear on the dome
- Ox-hoist inset is recognizable
- Ring closure narrows toward apex
- Lantern appears at top
- Final frame holds for 3 seconds
- All annotations are readable
- Color palette is consistent throughout

- [ ] **Step 3: Iterate on visual issues**

For each issue found in Step 2, fix the relevant rendering code. Common adjustments:
- Dome profile not looking right → tweak `geometry.py` arc calculations
- Text too small/large → adjust font sizes in `renderer.py` or `insets.py`
- Colors too dark/light → adjust values in `palette.py`
- Timing too fast/slow → adjust delays in `dome.py` FRAME_SEQUENCE
- Cutaway not clear → adjust shell thicknesses in `renderer.py`

After each fix, re-run `python dome.py` and re-check the GIF.

- [ ] **Step 4: Run all tests to ensure nothing broke**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 5: Optimize file size if needed**

If the GIF is over 15MB:

```bash
# Option 1: reduce colors
gifsicle --colors 128 -O3 output/brunelleschi_dome.gif -o output/brunelleschi_dome_optimized.gif

# Option 2: lossy compression
gifsicle -O3 --lossy=80 output/brunelleschi_dome.gif -o output/brunelleschi_dome_optimized.gif
```

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete Brunelleschi's dome construction GIF"
```

---

## Verification

1. **Run:** `python dome.py` — should produce `output/brunelleschi_dome.gif` without errors
2. **View:** Open GIF in browser — confirm ~25s loop with all 12 phases
3. **Check phases:** Title → drum → arch inset → shells → herringbone inset → courses → chain inset → ribs → ox-hoist inset → closure → lantern → final
4. **Check visuals:** Warm palette, readable annotations, clear cutaway structure
5. **Check size:** Under 15MB for blog embedding
6. **Tests:** `python -m pytest tests/ -v` — all pass
