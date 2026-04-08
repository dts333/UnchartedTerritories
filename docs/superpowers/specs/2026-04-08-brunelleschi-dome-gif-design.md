# Brunelleschi's Dome Construction GIF — Design Spec

## Purpose

Create an educational animated GIF depicting the construction of Brunelleschi's dome in Florence (1420–1436). The GIF teaches viewers about the architectural and engineering innovations through a frame-by-frame construction sequence with detailed teaching insets.

**Audience:** Educational blog / article readers.
**Output:** Single animated GIF, ~800×600px, moderate file size, self-contained with baked-in annotations.

## Stack

- **Python 3** with **pycairo** for frame rendering
- **imageio** (with Pillow plugin) for GIF assembly
- No other dependencies

## Visual Style

- **Illustrated / artistic** — warm Florentine palette, not clinical diagrams
- **Palette:** Dark brown background (`#2a1f14`), terracotta/sienna dome surfaces (`#c4663a`, `#a0522d`, `#8b4513`), gold accents and text (`#c4a35a`), cream for marble/stone (`#d4c5a9`), light text (`#e8d5b7`)
- **Unified palette** for both construction frames and inset detail frames — insets differentiate through content and framing, not color
- **Persistent half-cutaway:** Left half of dome shows exterior brick surface; right half shows internal structure (double shell, ribs, chain rings, herringbone pattern)

## Canvas Layout (800×600)

- **Top title bar:** "BUILDING BRUNELLESCHI'S DOME · 1420–1436" with gold text, thin gold border below
- **Main area:** Dome centered, split vertically — left labeled "EXTERIOR", right labeled "CUTAWAY"
- **Bottom annotation bar:** Floating text box with gold border explaining the current engineering principle
- **Inset frames:** Same canvas size, "DETAIL: [TITLE]" header, diagram in upper 2/3, explanatory text box in lower 1/3, "returning to construction..." footer

## Frame Sequence

| Phase | Frames | Delay | Content |
|-------|--------|-------|---------|
| 1. Title card | 1 | 2s | Title + dome silhouette |
| 2. Base octagon & drum | ~8 | 200ms | Octagonal base rises atop cathedral walls |
| 3. Inset: Pointed-fifth arch | 3 | 1.5s each | Semicircle vs pointed-fifth comparison with thrust vectors |
| 4. Inner & outer shells begin | ~6 | 200ms | Both shells start rising, gap visible on cutaway side |
| 5. Inset: Herringbone close-up | 3 | 1.5s each | Zoomed brick pattern — vertical bricks as locking "teeth" |
| 6. Herringbone courses rise | ~15 | 200ms | Courses spiral upward, cutaway shows brickwork |
| 7. Inset: Chain rings cross-section | 3 | 1.5s each | Radial slice showing stone/iron chains between shells |
| 8. Chain rings + ribs appear | ~8 | 200ms | 8 major + 16 minor ribs, chain rings at intervals |
| 9. Inset: Ox-hoist crane | 3 | 1.5s each | Reversible hoist with gear mechanism |
| 10. Progressive ring closure | ~15 | 200ms | Courses narrow toward oculus, self-supporting rings |
| 11. Lantern & oculus | ~6 | 200ms | Oculus cap, lantern rises |
| 12. Final reveal | 1 | 3s | Completed dome with summary annotations |

**Total: ~72 frames, ~25 seconds per loop**

## Dome Geometry

The dome uses a **pointed-fifth arch** profile:
- Two circular arcs, each with its center at 4/5 of the base diameter from the opposite side
- This produces a pointed profile (not semicircular) that is inherently more stable
- Modeled parametrically as a function `dome_profile(t) -> (x, y)` where `t` goes from 0 (base left) to 1 (base right), with the apex at t=0.5

The **octagonal base** is a regular octagon inscribed in the drum circle. Each of the 8 faces is a flat segment of the dome surface.

## Half-Cutaway Rendering

- Left half: Exterior surface rendered with brick-colored fill, subtle course lines, and terracotta gradients
- Right half: Cross-section showing:
  - **Outer shell** — thinner, brick-colored
  - **Gap** — empty space between shells
  - **Inner shell** — thicker, slightly different shade
  - **Ribs** — 8 major (at octagon corners) + 16 minor (2 per face), drawn as structural lines
  - **Chain rings** — horizontal bands at intervals, highlighted in gold
  - **Herringbone pattern** — visible on the cutaway brick face as alternating horizontal/vertical bricks
- The split line runs down the dome's vertical center axis

## Inset Detail Designs

### 1. Pointed-Fifth Arch Comparison
- Side-by-side: semicircular arch (left) vs pointed-fifth arch (right)
- Thrust vector arrows showing outward push differences
- Labels: "Needs scaffolding" vs "Self-supporting"
- Annotation: Why the pointed profile redirects forces more vertically

### 2. Herringbone Brickwork Close-Up
- Zoomed grid showing rows of horizontal bricks with vertical "spine" bricks at regular intervals
- Arrows indicating how vertical bricks act as teeth preventing slippage
- Annotation: Eliminates need for centering (wooden scaffold from below)

### 3. Chain Rings Cross-Section
- Radial slice through dome wall: outer shell, gap, inner shell
- Chain ring highlighted: sandstone links, iron clamps, wood tie-beams
- Annotation: "Like hoops on a barrel — resisting outward thrust"

### 4. Ox-Hoist Crane
- Side view: vertical shaft, ox at base walking in circle, gear mechanism, rope through dome opening
- Key callout: reversible gear — lift direction changes without turning oxen
- Annotation: First reversible gear in recorded history

## Project Structure

```
uncharted_territories/
├── dome.py              # Main entry point — orchestrates frame generation & GIF assembly
├── geometry.py          # Parametric dome profile, octagon math, coordinate helpers
├── renderer.py          # Cairo rendering — dome, bricks, ribs, chains, annotations
├── insets.py            # Four detail inset frame renderers
├── palette.py           # Color constants & gradient helpers
├── frames/              # Intermediate PNG output (gitignored)
└── output/              # Final GIF (gitignored)
```

### Module Responsibilities

- **`palette.py`** — Named color constants (BG, TERRACOTTA, SIENNA, GOLD, CREAM, TEXT), gradient helper functions
- **`geometry.py`** — `dome_profile(t)`, `octagon_points(radius)`, coordinate transforms, clipping region generators for exterior/cutaway halves
- **`renderer.py`** — `render_construction_frame(ctx, progress, phase)` draws the main dome view at a given construction progress; handles title bar, annotation bar, exterior/cutaway split rendering
- **`insets.py`** — `render_arch_comparison(ctx)`, `render_herringbone(ctx)`, `render_chain_rings(ctx)`, `render_ox_hoist(ctx)` — each draws one inset detail frame
- **`dome.py`** — Defines the frame sequence table (phase, count, delay), loops through generating PNGs via renderer/insets, assembles into GIF with imageio

## Verification

1. `pip install pycairo imageio[pillow]`
2. `python dome.py` — generates `frames/*.png` and `output/brunelleschi_dome.gif`
3. Verify: open GIF in browser, confirm ~25s loop, all 12 phases visible, annotations readable, cutaway structure clear
4. Check file size is reasonable for blog embedding (target < 15MB). If too large, optimize with `gifsicle -O3 --lossy=80` or reduce palette with `gifsicle --colors 128`
