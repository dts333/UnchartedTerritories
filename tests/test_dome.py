import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import dome


def test_frame_sequence_defined():
    """FRAME_SEQUENCE should produce a reasonable number of frames."""
    total_frames = sum(count for _, count, _ in dome.FRAME_SEQUENCE)
    assert 60 <= total_frames <= 100, f"Total frames {total_frames} outside expected range"


def test_generate_frames_returns_list():
    """generate_frames should return (surface, delay_ms) tuples."""
    frames = dome.generate_frames(limit=2)
    assert len(frames) >= 1
    surface, delay = frames[0]
    assert surface.get_width() == 800
    assert delay > 0
