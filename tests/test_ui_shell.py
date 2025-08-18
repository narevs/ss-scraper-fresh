import os

import pytest


# Attempt to import PyQt6; skip tests if the platform lacks the required
# graphical dependencies (e.g. missing ``libGL`` in headless containers).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")

try:  # pragma: no cover - import time guard
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QObject
except Exception as exc:  # pragma: no cover - handled by skip
    pytest.skip(f"PyQt6 not available: {exc}", allow_module_level=True)


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_required_widgets_exist(app):
    from app.ui_main_window import MainWindow

    window = MainWindow()
    object_names = [
        "backBtn",
        "fwdBtn",
        "reloadBtn",
        "homeBtn",
        "addressEdit",
        "goBtn",
        "ruleCombo",
        "siteCombo",
        "openCombo",
        "nSpin",
        "scrapeLinksBtn",
        "leftPanel",
        "pasteMenuBtn",
        "prefixEdit",
        "urlList",
        "leftFooter",
        "saveBtn",
        "prevBtn",
        "loadBtn",
        "nextBtn",
        "clearBtn",
        "scrapeBtn",
        "webView",
        "rightPanel",
        "emailList",
        "dataOptionsBtn",
        "clearEmailsBtn",
        "lblDataToday",
        "lblDataSession",
        "lblPagesToday",
        "lblPagesSession",
    ]

    for name in object_names:
        assert window.findChild(QObject, name) is not None, name

    splitter = window.splitter
    assert splitter.count() == 3
    assert splitter.childrenCollapsible() is False

