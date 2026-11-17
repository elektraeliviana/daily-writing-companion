"""
Smoke test for CustomTkinter UI App shell.
Verifies views, navigation, and window creation without errors.
"""

from src.ui.app import WritingCompanionApp


def test_ui_app_initialization_and_navigation():
    # Instantiate the application
    app = WritingCompanionApp()

    # Assert window title and registered views
    assert "Daily Writing Companion" in app.title()
    assert "write" in app.views
    assert "history" in app.views
    assert "stats" in app.views
    assert "settings" in app.views

    # Test navigating through all views
    for view_name in ["history", "stats", "settings", "write"]:
        app._select_view(view_name)

    # Clean shutdown
    if app.session:
        app.session.close()
    app.destroy()
