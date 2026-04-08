"""Color palette for Brunelleschi's dome animation.

All colors are (r, g, b) tuples with values 0.0-1.0, ready for Cairo's set_source_rgb.
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
