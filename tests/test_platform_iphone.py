from widgetable_solver.platform.iphone import _position_iphone_script


def test_position_script_only_uses_bottom_right_positioning():
    script = _position_iphone_script()

    assert 'menu item "Bottom Right"' in script
    assert 'keystroke "0" using command down' not in script
    assert 'menu item "Actual Size"' not in script
