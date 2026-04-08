import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import insets


def test_render_arch_comparison():
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
