import os

from devdeck_core.mock_deck_context import mock_context, assert_rendered

from devdeck.controls.command_control import CommandControl


class TestCommandControl:
    def test_initialize_sets_icon(self):
        # Get path to test-icon.png in the same directory as this test file
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-icon.png'))
        control = CommandControl(0, **{'icon': icon_path})
        with mock_context(control) as ctx:
            control.initialize()
            assert_rendered(ctx, icon_path)
