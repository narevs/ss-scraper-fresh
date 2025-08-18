from PyQt6.QtCore import QUrl

from app.navigation import navigate, to_qurl


class DummyView:
    def __init__(self):
        self.loaded = None

    def load(self, url):
        self.loaded = url


def test_to_qurl_returns_qurl():
    q = to_qurl("https://example.com")
    assert isinstance(q, QUrl)
    assert q.toString() == "https://example.com"


def test_navigate_accepts_string():
    view = DummyView()
    navigate(view, "https://example.com")
    assert isinstance(view.loaded, QUrl)
    assert view.loaded.toString() == "https://example.com"
