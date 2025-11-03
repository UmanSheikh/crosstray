"""Top-level package for CrossTray.

This module provides a lightweight library for creating system tray icons on Windows.
Future versions will expand to cross-platform support.
"""

__author__ = """Uman Sheikh"""
__email__ = 'muman014@gmail.com'
__version__ = '0.1.1'

# Expose public API
from .tray import MenuItem, Menu, Tray

__all__ = ['MenuItem', 'Menu', 'Tray']