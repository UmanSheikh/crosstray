"""Entry point for running CrossTray as a module (python -m crosstray)."""

import sys
from . import Tray  # Import from package

def demo() -> None:
    """Run a simple demo tray icon."""
    def on_click() -> None:
        print("Tray icon clicked!")

    tray: Tray = Tray(tooltip="CrossTray Demo")
    tray.on_click = on_click
    tray.add_menu_item("Print Hello", lambda: print("Hello from menu!"))
    tray.menu.add_separator()
    tray.add_menu_item("Quit", tray.quit)
    tray.run()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Delegate to cli.py if args are provided (assume it has a main() function)
        from .cli import main as cli_main
        cli_main()
    else:
        # Run demo if no args
        demo()