# Installation

CrossTray is available via PyPI and can be installed with pip. It requires Python 3.8+ and is currently Windows-only (v0.1.0 MVP). Future versions will add macOS and Linux support.

## Prerequisites

- Windows OS (for v0.1.0; cross-platform coming soon).
- Python 3.8 or higher.

## Stable Release

To install the latest stable version:

```bash
pip install crosstray
```

This will automatically install required dependencies like `pywin32` (on Windows) and `typer` (for the CLI).

## From Source (Development)

For the latest development version, clone the 
repository and install in editable mode:

```bash
git clone https://github.com/yourusername/crosstray.git
cd crosstray
pip install -e .
```

## Dependencies
CrossTray depends on:

- `pywin32` (Windows-specific for system tray integration).
- `typer` (for the CLI demo and utilities).

These are installed automatically via pip. For development/testing, install extras:

```bash
pip install crosstray[dev]
```

This adds `pytest` and others for running tests.

## Verification

After installation, verify with:
```bash
python -c "import crosstray; print(crosstray.__version__)"
```

Should output `0.1.0` (or your current version).

If issues arise (e.g., on non-Windows), the library will raise a `NotImplementedError`. Report bugs on GitHub.