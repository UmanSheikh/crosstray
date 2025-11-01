# Usage

CrossTray provides a simple API for creating system tray icons with menus and click handlers. Below are examples and API details for v0.1.0 (Windows-only).

## Quick Start

Run a demo via the CLI:

```bash
python -m crosstray demo --icon path/to/icon.ico --tooltip "My Tray"
```

This launches a basic tray icon with a menu.

## Basic Example

Here's a tested example script (save as my_tray_app.py and run with python my_tray_app.py):

```python
import crosstray as ct

def on_click() -> None:
    print("Tray icon clicked! Uman!")

tray = ct.Tray(icon="file.ico", title="My Tray App", tooltip="This is my tray application.")
tray.on_click = on_click
tray.add_menu_item("Say Hello", lambda: print("Hello from the tray menu!"))
tray.add_menu_item("Quit", tray.quit)
tray.run()
```

### Explanation:

- Import as ct for brevity.
- Create a Tray instance with optional icon (ICO recommended), title, and tooltip.
- Set on_click for left-click handling.
- Add menu items (right-click context menu) with labels and callbacks.
- Call run() to start the event loop (blocks until quit).

## API Overview
### Tray Class

- `__init__(icon: Optional[str] = None, title: Optional[str] = None, tooltip: str = "")`

  - Creates the tray icon. icon is a file path (falls back to default if missing).


- `add_menu_item(label: str, action: Callable[[], None]) -> Tray`

  - Adds a menu item with a callback; chainable.


- `run() -> None`

  - Starts the blocking event loop.


- `quit() -> None`

  - Cleans up and exits.


- Other methods: `refresh_icon()`, internal handlers.

### Menu Class

- `add_item(item: MenuItem) -> Menu`
- `add_separator() -> Menu`

### MenuItem Class

- `__init__(label: str, action: Callable[[], None], enabled: bool = True)`

For full details, see the source code or generated API docs (coming soon).

## CLI Usage
The package includes a CLI for demos and utilities:

```bash
python -m crosstray --help
```
- `demo`: Runs a sample tray (with `--icon` and `--tooltip` options).
- `--version`: Shows the version.

## Testing
Run unit tests with:
```bash
pytest
```
Tests cover classes like Tray, Menu, and MenuItem with mocks for GUI elements.

## Notes

- `v0.1.0` is MVP: Basic icons, menus, no async or notifications yet.
- Extend with your own callbacks for real apps (e.g., monitors, notifications).