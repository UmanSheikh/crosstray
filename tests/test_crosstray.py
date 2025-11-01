"""Tests for CrossTray library."""

import sys
from typing import Callable
import pytest
from unittest.mock import MagicMock, patch

from crosstray import MenuItem, Menu, Tray


@pytest.mark.skipif(sys.platform != 'win32', reason="Requires Windows platform")
class TestMenuItem:
    """Tests for MenuItem class."""

    def test_initialization(self) -> None:
        """Test MenuItem initialization with default values."""
        action: Callable[[], None] = lambda: print("Test")
        item = MenuItem(label="Test Label", action=action)
        assert item.label == "Test Label"
        assert item.action == action
        assert item.enabled is True

    def test_initialization_with_enabled_false(self) -> None:
        """Test MenuItem initialization with enabled=False."""
        action: Callable[[], None] = lambda: None
        item = MenuItem(label="Disabled", action=action, enabled=False)
        assert item.enabled is False


@pytest.mark.skipif(sys.platform != 'win32', reason="Requires Windows platform")
class TestMenu:
    """Tests for Menu class."""

    def test_initialization(self) -> None:
        """Test Menu initialization."""
        menu = Menu()
        assert menu.items == []

    def test_add_item(self) -> None:
        """Test adding a MenuItem."""
        menu = Menu()
        action: Callable[[], None] = lambda: None
        item = MenuItem("Item1", action)
        menu.add_item(item)
        assert len(menu.items) == 1
        assert menu.items[0] == item

    def test_add_separator(self) -> None:
        """Test adding a separator."""
        menu = Menu()
        menu.add_separator()
        assert len(menu.items) == 1
        assert menu.items[0] == "---"

    def test_chaining(self) -> None:
        """Test method chaining for add_item and add_separator."""
        menu = Menu()
        action: Callable[[], None] = lambda: None
        chained_menu = menu.add_item(MenuItem("Item", action)).add_separator()
        assert chained_menu is menu
        assert len(menu.items) == 2


@pytest.mark.skipif(sys.platform != 'win32', reason="Requires Windows platform")
class TestTray:
    """Tests for Tray class."""

    @patch('crosstray.tray.win32gui')
    @patch('crosstray.tray.win32api')
    @patch('crosstray.tray.win32con')
    @patch('crosstray.tray.win32gui_struct')
    @patch('crosstray.tray.os.path.isfile', return_value=True)
    def test_initialization(self, mock_isfile, mock_struct, mock_con, mock_api, mock_gui) -> None: # type: ignore
        """Test Tray initialization and window creation."""
        # Mock necessary calls to avoid actual GUI creation
        mock_gui.RegisterClass.return_value = 1  # type: ignore # Class atom
        mock_gui.CreateWindow.return_value = 123  # type: ignore # hwnd
        mock_api.GetModuleHandle.return_value = 456  # type: ignore # hinst
        mock_gui.LoadImage.return_value = 789  # type: ignore # hicon
        mock_gui.Shell_NotifyIcon.return_value = True # type: ignore

        tray = Tray(icon="test.ico", title="Test Title", tooltip="Test Tooltip")
        assert tray.icon == "test.ico"
        assert tray.title == "Test Title"
        assert tray.tooltip == "Test Tooltip"
        assert isinstance(tray.menu, Menu)
        assert tray.on_click is None
        assert tray.hwnd == 123
        assert tray.notify_id is not None
        assert tray.menu_actions == {}

    def test_add_menu_item(self) -> None:
        """Test adding a menu item via Tray."""
        # Since add_menu_item delegates to Menu, we can test without mocks
        tray = Tray()  # Note: This will create actual window on Windows; for CI, mock in real tests
        action: Callable[[], None] = lambda: None
        tray.add_menu_item("MenuItem", action)
        assert len(tray.menu.items) == 1
        assert tray.menu.items[0].label == "MenuItem" # type: ignore
        assert tray.menu.items[0].action == action # type: ignore

    @patch('crosstray.tray.win32gui')
    @patch('crosstray.tray.win32gui_struct')
    def test_build_menu(self, mock_struct, mock_gui) -> None: # type: ignore
        """Test _build_menu with mocks."""
        tray = Tray()
        action1: Callable[[], None] = lambda: print("Action1")
        action2: Callable[[], None] = lambda: print("Action2")
        tray.menu.add_item(MenuItem("Item1", action1))
        tray.menu.add_separator()
        tray.menu.add_item(MenuItem("Item2", action2))

        mock_gui.CreatePopupMenu.return_value = 999  # type: ignore # menu handle
        mock_struct.PackMENUITEMINFO.side_effect = [ # type: ignore
            ({"fSeparator": True}, None),  # Separator
            ({"text": "Item2", "wID": 1000}, None),  # Item2 (reverse order)
            ({"text": "Item1", "wID": 1001}, None),  # Item1
        ]
        mock_gui.InsertMenuItem.return_value = True # type: ignore

        menu_handle = tray._build_menu() # type: ignore
        assert menu_handle == 999
        assert len(tray.menu_actions) == 2
        assert tray.menu_actions[1000] == action2  # Due to reverse insertion
        assert tray.menu_actions[1001] == action1

    # Additional tests for handlers can be added with more mocking, e.g., for _on_notify
    @patch('crosstray.tray.win32gui')
    @patch('crosstray.tray.win32con')
    def test_on_notify(self, mock_con, mock_gui) -> None: # type: ignore
        """Test _on_notify handler with mocks."""
        tray = Tray()
        tray._show_menu = MagicMock() # type: ignore
        tray.on_click = MagicMock()

        # Simulate right-click
        tray._on_notify(123, 0, 0, mock_con.WM_RBUTTONUP) # type: ignore
        tray._show_menu.assert_called_once() # type: ignore

        # Simulate left-click
        tray._on_notify(123, 0, 0, mock_con.WM_LBUTTONUP) # type: ignore
        tray.on_click.assert_called_once()

        # Unknown lparam
        assert tray._on_notify(123, 0, 0, 999) is True  # type: ignore # Still returns True

    # Note: For run() and quit(), integration tests might require threading or subprocess
    # Example stub for integration test (run in Windows only, manually or with CI on Windows)
    # def test_run_and_quit_integration(self):
    #     import threading
    #     tray = Tray()
    #     thread = threading.Thread(target=tray.run)
    #     thread.start()
    #     time.sleep(1)  # Wait briefly
    #     tray.quit()
    #     thread.join(timeout=5)
    #     assert not thread.is_alive()