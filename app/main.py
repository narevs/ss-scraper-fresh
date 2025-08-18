"""Application entry point.

This module provides the :func:`main` function which initialises a Qt
application with a dark palette, constructs :class:`app.ui_main_window.MainWindow`
and displays it.  The function is also used by ``python -m app`` via
``app.__main__``.
"""

from __future__ import annotations

import os
import sys

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .ui_main_window import MainWindow


def _apply_dark_palette(app: QApplication) -> None:
    """Apply a basic dark theme to ``app``."""

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)


def main() -> None:
    """Run the SS Email Scraper application."""

    os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
    app = QApplication(sys.argv)
    _apply_dark_palette(app)

    window = MainWindow()
    window.show()
    window.navigate("https://www.google.com/")

    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()

