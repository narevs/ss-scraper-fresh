"""Simple non-blocking toast notifications."""
from __future__ import annotations

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt


def show_toast(parent, message: str, timeout: int = 3000) -> None:
    label = QLabel(message, parent)
    label.setWindowFlags(Qt.WindowType.ToolTip)
    label.show()
    QTimer.singleShot(timeout, label.close)
