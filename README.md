# CrossTray

[![PyPI version](https://badge.fury.io/py/crosstray.svg)](https://badge.fury.io/py/crosstray)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/crosstray.svg)](https://pypi.org/project/crosstray/)

A lightweight, unified Python library for creating system tray/menu bar icons across Windows, macOS, and Linux. No heavy GUI dependencies—just pure Python simplicity for status indicators, notifications, and menus.

### Why CrossTray?
- **Cross-Platform Magic**: Handles OS-specific quirks automatically (e.g., Windows notification area, macOS menu bar, Linux systray).
- **Minimal Footprint**: Dependency-free core (uses stdlib where possible, optional extras for icons/notifications).
- **Easy API**: Object-oriented and chainable, inspired by `pathlib` for intuitive use.
- **Async-Friendly**: Supports asyncio for real-time updates without blocking.

Perfect for building desktop utilities like monitors, trackers, or background apps.

### Installation
```bash
pip install crosstray
```

### Quick Start
```python
from crosstray import Tray

tray = Tray(icon="path/to/icon.png", title="My App")
tray.add_menu_item("Quit", lambda: tray.quit())
tray.run()
```
For more examples, see **Usage**.

---

### Features
- Create tray icons with custom images or text fallbacks.
- Build nested menus with callbacks.
- Show balloon notifications/toasts.
- Dynamic updates (e.g., change icon or menu on the fly).
- Event loop integration for async apps.
- Error handling for unsupported platforms.

---

### Usage

#### Basic Tray Icon
```python
from crosstray import Tray

def on_click(tray: ct.Tray):
    tray.send_notification("Tray Clicked", "You clicked the tray icon!", icon="file.ico", timeout=9000)

tray = Tray(icon="icon.ico", tooltip="Hello World")
tray.on_click = tray.on_click = lambda: on_click(tray)  # Or use tray.add_action("Click", on_click)
tray.run()  # Blocks until quit
```

#### With Menu
```python
from crosstray import Tray, MenuItem

tray = Tray(title="Status Monitor")

menu = tray.menu
menu.add_item(MenuItem("Refresh", lambda: print("Refreshing...")))
menu.add_separator()
submenu = menu.add_submenu("Settings")
submenu.add_item(MenuItem("Option 1", lambda: print("Selected 1")))
menu.add_item(MenuItem("Quit", tray.quit))

tray.run()
```

#### Async Example
```python
import asyncio
from crosstray import Tray

async def main():
    tray = Tray(icon="icon.png")
    tray.add_menu_item("Update", lambda: print("Updating"))

    # Simulate real-time update
    async def updater():
        while True:
            tray.tooltip = f"Time: {asyncio.get_event_loop().time()}"
            await asyncio.sleep(1)

    asyncio.create_task(updater())
    await tray.run_async()  # Non-blocking

asyncio.run(main())
```

---

### Contributing
Contributions welcome! Fork the repo, create a branch, and submit a PR. See `CONTRIBUTING.md` for guidelines.

### License
MIT License. See `LICENSE` for details.

Built with ❤️ by **Uman Sheikh**. Inspired by community needs for simpler desktop tools.
