"""Command-line interface for CrossTray.

This module provides a CLI entry point for running demos, showing version info,
and potentially other utilities as the library grows.
"""

import argparse

from crosstray import __version__
from crosstray.tray import Tray


def main() -> None:
    """
    Main CLI entry point.

    Parses arguments and dispatches to appropriate functions.
    """
    parser = argparse.ArgumentParser(
        description="CrossTray CLI: A lightweight system tray library for Windows."
    )
    parser.add_argument(
        "--version", action="version", version=f"CrossTray {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run a simple tray demo")
    demo_parser.add_argument(
        "--icon", type=str, default=None, help="Path to icon file (optional)"
    )
    demo_parser.add_argument(
        "--tooltip", type=str, default="CrossTray Demo", help="Tooltip text"
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo(icon=args.icon, tooltip=args.tooltip)
    else:
        parser.print_help()
        exit(0)


def run_demo(icon: str | None = None, tooltip: str = "CrossTray Demo") -> None:
    """
    Run a demonstration of the Tray functionality.

    Args:
        icon (str | None, optional): Path to icon file. Defaults to None.
        tooltip (str, optional): Tooltip text. Defaults to "CrossTray Demo".
    """
    def on_click() -> None:
        print("Tray icon clicked!")

    tray = Tray(icon=icon, tooltip=tooltip)
    tray.on_click = on_click
    tray.add_menu_item("Print Hello", lambda: print("Hello from menu!"))
    tray.menu.add_separator()
    tray.add_menu_item("Quit", tray.quit)
    tray.run()


if __name__ == "__main__":
    main()