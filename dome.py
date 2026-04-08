"""Main entry point for Brunelleschi's dome project.

Still exposes the original frame generation helpers for the animated GIF, but
the default build now produces a static interactive explorer page with a
clickable dome overview and separate teaching insets.
"""
import os
import cairo
import numpy as np
from PIL import Image

import explorer
import renderer
import insets

# Frame sequence: (phase, frame_count, delay_ms)
# Negative phases are insets:
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

INSET_RENDERERS = {
    -1: insets.render_arch_comparison,
    -2: insets.render_herringbone,
    -3: insets.render_chain_rings,
    -4: insets.render_ox_hoist,
}


def _surface_to_numpy(surface: cairo.ImageSurface) -> np.ndarray:
    """Convert a Cairo ARGB32 surface to a numpy RGB array."""
    buf = surface.get_data()
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(
        surface.get_height(), surface.get_width(), 4
    ).copy()
    # Cairo BGRA -> RGB
    rgb = np.empty((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    rgb[:, :, 0] = arr[:, :, 2]  # R
    rgb[:, :, 1] = arr[:, :, 1]  # G
    rgb[:, :, 2] = arr[:, :, 0]  # B
    return rgb


def generate_frames(limit: int = None) -> list[tuple[cairo.ImageSurface, int]]:
    """Generate all frames as (surface, delay_ms) tuples."""
    frames = []
    sequence = FRAME_SEQUENCE[:limit] if limit else FRAME_SEQUENCE

    for phase, count, delay in sequence:
        if phase < 0:
            # Inset — render once, repeat count times
            surface = INSET_RENDERERS[phase]()
            for _ in range(count):
                frames.append((surface, delay))
        elif phase == 1:
            # Title card
            surface = renderer.render_construction_frame(progress=0.0, phase=2)
            frames.append((surface, delay))
        elif phase == 12:
            # Final reveal
            surface = renderer.render_construction_frame(progress=1.0, phase=12)
            frames.append((surface, delay))
        else:
            # Construction phase
            for i in range(count):
                progress = i / max(count - 1, 1)
                surface = renderer.render_construction_frame(progress=progress, phase=phase)
                frames.append((surface, delay))

    return frames


def assemble_gif(frames: list[tuple[cairo.ImageSurface, int]], output_path: str):
    """Assemble frames into an animated GIF using Pillow for reliable timing."""
    pil_frames = []

    for surface, delay_ms in frames:
        rgb = _surface_to_numpy(surface)
        pil_frames.append((Image.fromarray(rgb), delay_ms))

    if not pil_frames:
        return

    first_img, first_delay = pil_frames[0]
    # Convert to P mode (palette) for GIF
    first_gif = first_img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    rest_gifs = []
    rest_durations = []
    for img, delay in pil_frames[1:]:
        rest_gifs.append(img.quantize(colors=256, method=Image.Quantize.MEDIANCUT))
        rest_durations.append(delay)

    first_gif.save(
        output_path,
        save_all=True,
        append_images=rest_gifs,
        duration=[first_delay] + rest_durations,
        loop=0,
        optimize=False,
    )


def main():
    """Build the interactive explorer bundle."""
    os.makedirs("output", exist_ok=True)
    output_path = explorer.build_interactive_explorer()
    print(f"Built interactive explorer: {output_path}")
    print("Open index.html in a browser and click the dome hotspots to switch insets.")


if __name__ == "__main__":
    main()
