"""Navigation helpers for SS Scraper."""
from __future__ import annotations

from PyQt6.QtCore import QUrl, QEventLoop, QTimer


def to_qurl(url: str) -> QUrl:
    """Return a QUrl using Qt's tolerant parser."""
    return QUrl.fromUserInput(url)


def navigate(view, url: str | QUrl) -> QUrl:
    """Navigate the given Qt view to *url*.

    Parameters
    ----------
    view: Any object with a ``load`` method accepting ``QUrl``.
    url: String or ``QUrl`` to navigate to.
    """
    qurl = to_qurl(url) if isinstance(url, str) else url
    if hasattr(view, "load"):
        view.load(qurl)
    return qurl


def wait_for_load(view, timeout: int = 15000) -> bool:
    """Block until the Qt web view has finished loading or ``timeout`` ms."""
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    try:
        view.loadFinished.connect(loop.quit)
    except Exception:
        # No signal available; return immediately
        return False
    timer.start(timeout)
    loop.exec()
    finished = timer.isActive()
    timer.stop()
    return finished
