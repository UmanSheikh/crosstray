"""Core module for CrossTray's system tray functionality."""

import sys
import os
from typing import Callable, Optional, Dict, Any, Tuple

# Import Windows-specific modules from pywin32
import win32api
import win32con
import win32gui
import win32gui_struct

# Constants for notifications
NIIF_USER = 4
NOTIFYICON_VERSION = 4  # Use 4 for hBalloonIcon support (NOTIFYICON_VERSION_4)

# Platform check: Ensure the library is only used on Windows for this version
if sys.platform != 'win32':
    raise NotImplementedError("CrossTray v0.1.0 supports only Windows. Future versions will add macOS and Linux.")


class MenuItem:
    """Represents a single item in the system tray menu.

    This class encapsulates a menu item's label, action (callback), and enabled state.
    """

    def __init__(self, label: str, action: Callable[[], None], enabled: bool = True) -> None:
        """
        Initialize a MenuItem.

        Args:
            label (str): The text displayed for the menu item.
            action (Callable[[], None]): The callback function to execute when the item is clicked.
            enabled (bool, optional): Whether the menu item is enabled. Defaults to True.
        """
        self.label: str = label  # Display text for the menu item
        self.action: Callable[[], None] = action  # Callback to invoke on click
        self.enabled: bool = enabled  # Flag to enable/disable the item (not implemented in MVP)


class Menu:
    """Manages a collection of menu items for the system tray.

    This class allows adding items and separators to build a context menu.
    """

    def __init__(self) -> None:
        """Initialize an empty Menu."""
        self.items: list[MenuItem | str] = []  # List of MenuItem objects or "---" for separators

    def add_item(self, item: MenuItem) -> 'Menu':
        """
        Add a MenuItem to the menu.

        Args:
            item (MenuItem): The menu item to add.

        Returns:
            Menu: The menu instance for method chaining.
        """
        self.items.append(item)  # Append the item to the internal list
        return self  # Enable chaining (e.g., menu.add_item(...).add_separator())

    def add_separator(self) -> 'Menu':
        """
        Add a separator to the menu.

        Returns:
            Menu: The menu instance for method chaining.
        """
        self.items.append("---")  # Use "---" as a sentinel value for separators
        return self  # Enable chaining


class Tray:
    """Main class for creating and managing a system tray icon on Windows.

    This class handles the creation of the tray icon, menu integration, event handling,
    and lifecycle methods like run and quit.
    """

    def __init__(self, icon: Optional[str] = None, title: Optional[str] = None, tooltip: str = "") -> None:
        """
        Initialize a Tray instance.

        Args:
            icon (Optional[str], optional): Path to the icon file (ICO format recommended). Defaults to None.
            title (Optional[str], optional): Fallback title if no icon is provided. Defaults to "CrossTray".
            tooltip (str, optional): Tooltip text shown on hover. Defaults to "".
        """
        self.icon: Optional[str] = icon  # Path to the icon image file
        self.title: str = title or "CrossTray"  # Default title if not provided
        self.tooltip: str = tooltip  # Hover text for the tray icon
        self.menu: Menu = Menu()  # Associated menu for right-click context
        self.on_click: Optional[Callable[[], None]] = None  # Callback for left-click on icon
        self.hwnd: Optional[int] = None  # Handle to the hidden window for message processing
        self.notify_id: Optional[Tuple[Any, ...]] = None  # Notification ID for Shell_NotifyIcon
        self.menu_actions: Dict[int, Callable[[], None]] = {}  # Mapping of menu IDs to actions
        self._create_window()  # Set up the underlying window and message map

    def _create_window(self) -> None:
        """Create a hidden window for handling Windows messages.

        This method sets up the window class, registers it, and creates the window instance.
        It also initializes the message map for event handling.
        """
        # Define the message map: Maps Windows messages to handler methods
        message_map: Dict[int, Callable[..., Any]] = {
            win32con.WM_DESTROY: self._on_destroy,  # Handle window destruction
            win32con.WM_COMMAND: self._on_command,  # Handle menu commands
            win32con.WM_USER + 20: self._on_notify,  # Custom message for tray notifications
            win32gui.RegisterWindowMessage("TaskbarCreated"): self._on_restart,  # Handle taskbar recreation (e.g., Explorer restart) # type: ignore
        }

        # Create and register the window class
        wc: win32gui.WNDCLASS = win32gui.WNDCLASS()  # type: ignore # Window class structure
        wc.hInstance = win32api.GetModuleHandle(None)  # Current module handle
        wc.lpszClassName = "CrossTrayWin"  # Unique class name
        wc.lpfnWndProc = message_map  # Procedure to handle messages
        class_atom: int = win32gui.RegisterClass(wc)  # type: ignore # Register the class

        # Create the hidden window
        self.hwnd = win32gui.CreateWindow(
            class_atom, "CrossTrayWin", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None # type: ignore
        ) 
        self.refresh_icon()  # Add or update the tray icon immediately

    def refresh_icon(self) -> None:
        """Refresh or add the tray icon in the notification area.

        Loads the icon (or default), sets up the notification structure, and calls Shell_NotifyIcon.
        """
        hinst: int = win32api.GetModuleHandle(None)  # Module handle for loading resources
        hicon: int = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)  # type: ignore # Default system icon if none provided
        if self.icon and os.path.isfile(self.icon):
            # Load custom icon from file
            hicon = win32gui.LoadImage(hinst, self.icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE) # type: ignore

        # Determine if adding or modifying the icon
        message: int = win32gui.NIM_ADD if not self.notify_id else win32gui.NIM_MODIFY
        # Notification structure: (hwnd, id, flags, callback_message, icon, tooltip)
        self.notify_id = (
            self.hwnd, 0, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
            win32con.WM_USER + 20, hicon, self.tooltip
        )
        win32gui.Shell_NotifyIcon(message, self.notify_id)  # type: ignore # Apply the notification

    def add_menu_item(self, label: str, action: Callable[[], None]) -> 'Tray':
        """
        Add a menu item to the tray's menu.

        Args:
            label (str): The label for the menu item.
            action (Callable[[], None]): The callback to execute on click.

        Returns:
            Tray: The tray instance for method chaining.
        """
        self.menu.add_item(MenuItem(label, action))  # Delegate to Menu's add_item
        # Note: In MVP, menu is rebuilt on show; no live update needed here
        return self  # Enable chaining (e.g., tray.add_menu_item(...).run())

    def _build_menu(self) -> int:
        """Build the popup menu from the current menu items.

        Creates a Windows popup menu, assigns IDs to items, and maps actions.

        Returns:
            int: Handle to the created menu.
        """
        menu: int = win32gui.CreatePopupMenu() # type: ignore # Create an empty popup menu
        action_id: int = 1000  # Starting ID for menu items (arbitrary, but above system IDs)
        self.menu_actions = {}  # Reset action mapping
        # Iterate in reverse to insert items at position 0 (builds top-to-bottom)
        for item in self.menu.items[::-1]:
            if item == "---":
                # Add separator
                item_struct, _ = win32gui_struct.PackMENUITEMINFO(fSeparator=True) # type: ignore
                win32gui.InsertMenuItem(menu, 0, True, item_struct) # type: ignore
            else:
                # Add regular item
                self.menu_actions[action_id] = item.action  # type: ignore # Map ID to callback
                item_struct, _ = win32gui_struct.PackMENUITEMINFO(text=item.label, wID=action_id) # type: ignore
                win32gui.InsertMenuItem(menu, 0, True, item_struct) # type: ignore
                action_id += 1  # Increment ID for next item
        return menu # type: ignore

    def _show_menu(self) -> None:
        """Display the context menu at the current cursor position.

        Builds the menu, tracks it as a popup, and handles cleanup.
        """
        pos: Tuple[int, int] = win32gui.GetCursorPos()  # Get current mouse position
        win32gui.SetForegroundWindow(self.hwnd)  # type: ignore # Bring window to foreground for menu focus
        menu: int = self._build_menu()  # Construct the menu
        # Show the popup menu at cursor position
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None) # type: ignore
        # Post a null message to release resources
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def _on_notify(self, hwnd: int, msg: int, wparam: int, lparam: int) -> bool:
        """Handler for tray notification messages.

        Responds to left/right clicks on the icon.

        Args:
            hwnd (int): Window handle.
            msg (int): Message code.
            wparam (int): WPARAM.
            lparam (int): LPARAM (event type).

        Returns:
            bool: True to indicate handled.
        """
        if lparam == win32con.WM_RBUTTONUP:
            self._show_menu()  # Show menu on right-click
        elif lparam == win32con.WM_LBUTTONUP and self.on_click:
            self.on_click()  # Invoke left-click callback if set
        return True  # Message handled

    def _on_command(self, hwnd: int, msg: int, wparam: int, lparam: int) -> None:
        """Handler for menu command messages.

        Executes the action associated with the selected menu item.

        Args:
            hwnd (int): Window handle.
            msg (int): Message code.
            wparam (int): WPARAM (contains command ID).
            lparam (int): LPARAM.
        """
        cmd_id: int = win32gui.LOWORD(wparam) # type: ignore # Extract low word for command ID
        if cmd_id in self.menu_actions:
            self.menu_actions[cmd_id]()  # Invoke the mapped action

    def _on_destroy(self, hwnd: int, msg: int, wparam: int, lparam: int) -> None:
        """Handler for WM_DESTROY message.

        Cleans up the tray icon and posts quit message.

        Args:
            hwnd (int): Window handle.
            msg (int): Message code.
            wparam (int): WPARAM.
            lparam (int): LPARAM.
        """
        nid: Tuple[int, int] = (self.hwnd, 0)  # type: ignore # Notification ID to delete
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid) # type: ignore # Remove icon from tray
        win32gui.PostQuitMessage(0)  # Signal to exit the message loop

    def _on_restart(self, *args: Any) -> None:
        """Handler for taskbar recreation (e.g., Explorer restart).

        Re-adds the tray icon.

        Args:
            *args: Variable arguments from message proc.
        """
        self.notify_id = None  # Reset notify ID
        self.refresh_icon()  # Re-add the icon

    def send_notification(self, title: str, msg: str, icon: str, timeout: int) -> None:
        """Send a balloon notification from the tray icon.

        Args:
            title (str): Title of the notification.
            msg (str): Message body of the notification.
            icon (str): Path to the icon file.
            timeout (int): Duration in milliseconds to display the notification.
        """
        if not self.hwnd:
            raise RuntimeError("Tray not initialized")

        if not os.path.isfile(icon):
            raise ValueError(f"Icon file not found: {icon}")

        hinst = win32api.GetModuleHandle(None)
        h_balloon_icon = win32gui.LoadImage( # type: ignore
            hinst, icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        )

        timeout = max(5000, min(timeout, 30000))  # Clamp timeout between 5s and 30s

        nid = (
            self.hwnd, 
            0, win32gui.NIF_INFO, 
            win32con.WM_USER + 20,
            0, 
            self.tooltip, 
            msg, 
            timeout, 
            title, 
            NIIF_USER
        )

        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid) # type: ignore

    def run(self) -> None:
        """Start the message pump to handle events.

        This method blocks until the window is destroyed (e.g., via quit).
        """
        win32gui.PumpMessages()  # Enter the Windows message loop

    def quit(self) -> None:
        """Quit the tray application.

        Destroys the window, which triggers cleanup.
        """
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)  # Destroy the hidden window