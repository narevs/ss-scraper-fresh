"""Qt UI for Scholar Summit Email Scraper.

This module implements a minimal version of the locked UI described in the
specification. The widgets and signal wiring are provided so that the
application can launch and basic navigation works. Many features are stubs in
this educational implementation.
"""
from __future__ import annotations

from typing import List

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QMenu,
)

try:  # pragma: no cover - optional in test env
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover
    QWebEngineView = QLabel  # type: ignore

from .navigation import navigate
from .sites import SITES


class MainWindow(QMainWindow):
    """Main application window following the locked layout."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SS Scraper")

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        self.setCentralWidget(splitter)

        # Panels
        self.queue_panel = QWidget()
        self.browser_panel = QWidget()
        self.data_panel = QWidget()
        splitter.addWidget(self.queue_panel)
        splitter.addWidget(self.browser_panel)
        splitter.addWidget(self.data_panel)
        splitter.setSizes([320, 900, 360])

        self._setup_queue_panel()
        self._setup_browser_panel()
        self._setup_data_panel()

        # Settings
        self.settings = QSettings("ScholarSummit", "SS_Scraper")
        self._restore_settings()
        navigate(self.view, "https://www.google.com")

    # ------------------------------------------------------------------
    # Setup helpers
    def _setup_queue_panel(self) -> None:
        layout = QVBoxLayout(self.queue_panel)

        # Toolbar
        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)
        self.paste_btn = QToolButton(text="Paste")
        self.paste_menu = QMenu(self.paste_btn)
        for action in ["Paste", "Split", "Dedup", "Import .txt/.csv"]:
            self.paste_menu.addAction(action)
        self.paste_btn.setMenu(self.paste_menu)
        self.paste_btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        toolbar.addWidget(self.paste_btn)

        self.prefix_edit = QLineEdit()
        self.prefix_edit.setPlaceholderText("Prefix")
        toolbar.addWidget(self.prefix_edit)

        # URL queue
        self.url_list = QListWidget()
        layout.addWidget(self.url_list)

        # Footer buttons
        footer = QHBoxLayout()
        layout.addLayout(footer)
        self.save_btn = QPushButton("Save")
        self.prev_btn = QPushButton("Prev")
        self.load_btn = QPushButton("Load")
        self.next_btn = QPushButton("Next")
        self.clear_btn = QPushButton("Clear")
        self.scrape_btn = QPushButton("Scrape")
        for w in [self.save_btn, self.prev_btn, self.load_btn, self.next_btn, self.clear_btn, self.scrape_btn]:
            footer.addWidget(w)

    def _setup_browser_panel(self) -> None:
        layout = QVBoxLayout(self.browser_panel)

        # Address line
        line1 = QHBoxLayout()
        layout.addLayout(line1)
        self.address_bar = QLineEdit()
        self.go_btn = QPushButton("Go")
        line1.addWidget(self.address_bar)
        line1.addWidget(self.go_btn)

        # Controls line
        line2 = QHBoxLayout()
        layout.addLayout(line2)
        self.back_btn = QPushButton("◀")
        self.forward_btn = QPushButton("▶")
        self.reload_btn = QPushButton("⟳")
        self.home_btn = QPushButton("⌂")
        self.rule_combo = QComboBox()
        self.site_combo = QComboBox()
        self.open_btn = QPushButton("Open")
        self.n_spin = QSpinBox()
        self.n_spin.setMinimum(1)
        self.n_spin.setValue(10)
        self.scrape_links_btn = QPushButton("Scrape Links")
        for w in [
            self.back_btn,
            self.forward_btn,
            self.reload_btn,
            self.home_btn,
            self.rule_combo,
            self.site_combo,
            self.open_btn,
            self.n_spin,
            self.scrape_links_btn,
        ]:
            line2.addWidget(w)

        # Web view
        self.view = QWebEngineView()
        layout.addWidget(self.view)

        # Status pill and progress
        status_layout = QHBoxLayout()
        layout.addLayout(status_layout)
        self.status_label = QLabel("Idle")
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress)

        # Signal wiring
        self.address_bar.returnPressed.connect(self._nav_from_bar)
        self.go_btn.clicked.connect(self._nav_from_bar)
        self.open_btn.clicked.connect(self._nav_from_bar)
        self.home_btn.clicked.connect(self._nav_home)
        self.rule_combo.currentIndexChanged.connect(self._rule_changed)
        self.site_combo.currentIndexChanged.connect(self._site_changed)
        self.scrape_links_btn.clicked.connect(self._scrape_links)

        # Populate rule/site combos with placeholder data
        self.rule_combo.addItem("Default")
        for s in SITES:
            self.site_combo.addItem(s.label)

    def _setup_data_panel(self) -> None:
        layout = QVBoxLayout(self.data_panel)
        layout.addWidget(QLabel("Collected Data"))
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["Email"])
        layout.addWidget(self.table)

        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)
        self.data_options = QComboBox()
        self.data_options.addItems(["CSV", "Excel", "Copy"])
        self.clear_data_btn = QPushButton("Clear")
        toolbar.addWidget(self.data_options)
        toolbar.addWidget(self.clear_data_btn)

        layout.addWidget(QLabel("Stats"))
        self.stats_label = QLabel("Data Collected: 0\nPages Visited: 0")
        layout.addWidget(self.stats_label)

        filter_layout = QHBoxLayout()
        layout.addLayout(filter_layout)
        self.unique_only = QCheckBox("Unique only")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search")
        filter_layout.addWidget(self.unique_only)
        filter_layout.addWidget(self.search_box)

    # ------------------------------------------------------------------
    # Signal handlers (mostly stubs)
    def _nav_from_bar(self) -> None:
        navigate(self.view, self.address_bar.text())

    def _nav_home(self) -> None:
        self.address_bar.setText("https://www.google.com")
        navigate(self.view, "https://www.google.com")

    def _rule_changed(self, idx: int) -> None:  # pragma: no cover - UI logic
        pass

    def _site_changed(self, idx: int) -> None:  # pragma: no cover - UI logic
        try:
            site = SITES[idx]
        except IndexError:
            return
        self.address_bar.setText(site.base_url)
        navigate(self.view, site.base_url)

    def _scrape_links(self) -> None:  # pragma: no cover - UI logic
        pass

    # ------------------------------------------------------------------
    # Settings
    def closeEvent(self, event) -> None:  # pragma: no cover - GUI
        self._save_settings()
        super().closeEvent(event)

    def _save_settings(self) -> None:
        self.settings.setValue("splitter", self.centralWidget().sizes())
        self.settings.setValue("address", self.address_bar.text())

    def _restore_settings(self) -> None:
        splitter: QSplitter = self.centralWidget()  # type: ignore[assignment]
        sizes = self.settings.value("splitter")
        if sizes:
            splitter.setSizes([int(s) for s in sizes])
        addr = self.settings.value("address")
        if addr:
            self.address_bar.setText(addr)
