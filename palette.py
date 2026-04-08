"""Color palette for Brunelleschi's dome animation.

All colors are (r, g, b) tuples with values 0.0-1.0, ready for Cairo's set_source_rgb.
Hex references in comments for visual identification.
"""

# Background
BG = (0.165, 0.122, 0.078)            # #2a1f14
SKY_TOP = (0.137, 0.086, 0.063)       # #231610
SKY_BOTTOM = (0.251, 0.165, 0.110)    # #402a1c
GLOW = (0.592, 0.349, 0.165)          # #97592a

# Dome surfaces
TERRACOTTA = (0.769, 0.400, 0.227)    # #c4663a
SIENNA = (0.627, 0.322, 0.176)        # #a0522d
DARK_BROWN = (0.545, 0.271, 0.075)    # #8b4513
BRICK_LIGHT = (0.851, 0.522, 0.314)   # #d98550
BRICK_SHADOW = (0.408, 0.220, 0.118)  # #68381e

# Structural
DRUM_STONE = (0.478, 0.384, 0.282)    # #7a6248
RIB_DARK = (0.353, 0.275, 0.220)      # #5a4638
STONE_LIGHT = (0.882, 0.835, 0.733)   # #e1d5bb
STONE_SHADOW = (0.357, 0.282, 0.208)  # #5b4835

# Accents
GOLD = (0.769, 0.639, 0.353)          # #c4a35a
CREAM = (0.831, 0.773, 0.663)         # #d4c5a9
TEXT = (0.910, 0.835, 0.718)          # #e8d5b7
TEXT_MUTED = (0.792, 0.725, 0.620)    # #cab99e

# UI elements
ANNOTATION_BG = (0.227, 0.184, 0.122) # #3a2f1f
PANEL = (0.184, 0.145, 0.098)         # #2f2519
PANEL_ALT = (0.286, 0.216, 0.149)     # #493726
VOID = (0.090, 0.067, 0.051)          # #17110d


def set_color(ctx, color):
    """Set Cairo source color from a palette tuple."""
    ctx.set_source_rgb(*color)


def set_color_alpha(ctx, color, alpha):
    """Set Cairo source color with alpha from a palette tuple."""
    ctx.set_source_rgba(color[0], color[1], color[2], alpha)
