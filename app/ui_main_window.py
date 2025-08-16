from PyQt6.QtCore import Qt, QSize, QSettings, QUrl
from PyQt6.QtGui import QPalette, QColor, QGuiApplication, QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QToolButton, QComboBox, QSpinBox, QSplitter, QListWidget, QTextEdit, QLabel,
    QFrame, QListWidgetItem, QFileDialog, QMenu, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
import csv
import json
import os
from datetime import datetime

APP_TITLE = "SS Email Scraper — Step 4"

def to_qurl(url: str) -> QUrl:
    return QUrl.fromUserInput(url or "")

def dedup_preserve_order(strings, key=lambda s: s.lower().strip()):
    seen = set()
    out = []
    for s in strings:
        k = key(s)
        if k and k not in seen:
            seen.add(k)
            out.append(s)
    return out

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1520, 900)
        self._settings = QSettings()

        self._init_dark_theme()
        self._build_ui()
        self._restore_state()
        self._navigate("https://www.google.com/")

    # ---------- THEME ----------
    def _init_dark_theme(self):
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        pal.setColor(QPalette.ColorRole.Base, QColor(24, 24, 24))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 35, 35))
        pal.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        pal.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(53, 132, 228))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(pal)
        self.setStyleSheet("""
            QLineEdit, QComboBox, QSpinBox, QTextEdit, QListWidget {
                background:#1E1E1E; color:#E0E0E0; border:1px solid #3A3A3A; border-radius:8px; padding:6px;
            }
            QPushButton, QToolButton {
                background:#2B2B2B; color:#E8E8E8; border:1px solid #3A3A3A; border-radius:10px; padding:6px 10px;
            }
            QPushButton:hover, QToolButton:hover { border-color:#5A5A5A; }
            QFrame#panelTitle { color:#A0A0A0; font-weight:600; }
            QSplitter::handle { background:#3A3A3A; }
        """)

    # ---------- UI BUILD ----------
    def _build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        # Header Line 1: Address bar
        addr_row = QHBoxLayout()
        self.address = QLineEdit()
        self.address.setPlaceholderText("Enter URL and press Enter…")
        self.address.returnPressed.connect(self._on_address_enter)
        addr_row.addWidget(self.address)
        root_layout.addLayout(addr_row)

        # Header Line 2: Nav + selectors
        hdr_row = QHBoxLayout()
        self.btn_back   = self._tool("◀", "Back", self._on_back)
        self.btn_fwd    = self._tool("▶", "Forward", self._on_forward)
        self.btn_reload = self._tool("⟳", "Reload", self._on_reload)
        self.btn_home   = self._tool("⌂", "Home", self._on_home)
        for b in (self.btn_back, self.btn_fwd, self.btn_reload, self.btn_home):
            hdr_row.addWidget(b)
        hdr_row.addWidget(self._sep())

        self.rule = QComboBox(); self.rule.setPlaceholderText("Rule")
        self.site = QComboBox(); self.site.setPlaceholderText("Site")
        self.open_btn = QPushButton("Open"); self.open_btn.clicked.connect(self._on_open_clicked)
        n_label = QLabel("N"); n_label.setObjectName("panelTitle")
        self.n_spin = QSpinBox(); self.n_spin.setRange(1, 500); self.n_spin.setValue(50)
        self.scrape_btn = QPushButton("Scrape Links"); self.scrape_btn.clicked.connect(self._noop)  # Step 5 later

        hdr_row.addWidget(self.rule)
        hdr_row.addWidget(self.site)
        hdr_row.addWidget(self.open_btn)
        hdr_row.addWidget(n_label)
        hdr_row.addWidget(self.n_spin)
        hdr_row.addWidget(self.scrape_btn)
        root_layout.addLayout(hdr_row)

        # Splitter: Left | Middle | Right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self.splitter = splitter

        # ----- LEFT PANEL -----
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(6,6,6,6); ll.setSpacing(8)
        lbl_left = QLabel("URL Queue"); lbl_left.setObjectName("panelTitle")
        ll.addWidget(lbl_left)

        # Paste menu row
        paste_row = QHBoxLayout()
        self.prefix_edit = QLineEdit(); self.prefix_edit.setPlaceholderText("Prefix Text (optional)")
        self.btn_paste_menu = QPushButton("Paste ▾")
        self.btn_paste_menu.setObjectName("pasteMenuBtn")
        menu = QMenu(self)
        act_paste = QAction("Paste", self); act_paste.triggered.connect(self._act_paste)
        act_split = QAction("Split (lines → URLs)", self); act_split.triggered.connect(self._act_split)
        act_dedup = QAction("Dedup", self); act_dedup.triggered.connect(self._act_dedup)
        act_import = QAction("Import (txt/csv)", self); act_import.triggered.connect(self._act_import)
        menu.addAction(act_paste); menu.addAction(act_split); menu.addAction(act_dedup); menu.addSeparator(); menu.addAction(act_import)
        self.btn_paste_menu.setMenu(menu)
        paste_row.addWidget(self.btn_paste_menu)
        paste_row.addWidget(self.prefix_edit)
        ll.addLayout(paste_row)

        self.url_list = QListWidget()
        ll.addWidget(self.url_list, 1)

        # Footer controls
        foot = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_prev = QPushButton("Prev")
        self.btn_load = QPushButton("Load")
        self.btn_next = QPushButton("Next")
        self.btn_clear = QPushButton("Clear")
        self.btn_scrape_footer = QPushButton("Scrape")
        foot.addWidget(self.btn_save); foot.addWidget(self.btn_prev); foot.addWidget(self.btn_load)
        foot.addWidget(self.btn_next); foot.addWidget(self.btn_clear); foot.addWidget(self.btn_scrape_footer)
        ll.addLayout(foot)

        # Wire footer actions
        self.btn_save.clicked.connect(self._save_queue)
        self.btn_load.clicked.connect(self._load_queue)
        self.btn_prev.clicked.connect(self._select_prev)
        self.btn_next.clicked.connect(self._select_next)
        self.btn_clear.clicked.connect(self._clear_queue)
        self.btn_scrape_footer.clicked.connect(self._noop)  # Step 5 later

        # ----- MIDDLE (BROWSER) -----
        mid = QWidget(); ml = QVBoxLayout(mid); ml.setContentsMargins(6,6,6,6); ml.setSpacing(8)
        lbl_mid = QLabel("Browser"); lbl_mid.setObjectName("panelTitle")
        self.web = QWebEngineView()
        ml.addWidget(lbl_mid); ml.addWidget(self.web)

        # ----- RIGHT PANEL -----
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(6,6,6,6); rl.setSpacing(8)
        lbl_right = QLabel("Collected Data (emails only)"); lbl_right.setObjectName("panelTitle")
        self.data_view = QListWidget()
        rl.addWidget(lbl_right)
        rl.addWidget(self.data_view, 1)

        # Data Options row
        data_row = QHBoxLayout()
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_xlsx = QPushButton("Export Excel")
        self.btn_copy = QPushButton("Copy")
        self.btn_data_clear = QPushButton("Clear")
        data_row.addWidget(self.btn_export_csv); data_row.addWidget(self.btn_export_xlsx)
        data_row.addWidget(self.btn_copy); data_row.addWidget(self.btn_data_clear)
        rl.addLayout(data_row)

        # Stats
        stats_title = QLabel("Stats"); stats_title.setObjectName("panelTitle")
        self.stats_text = QTextEdit(); self.stats_text.setReadOnly(True); self.stats_text.setFixedHeight(140)
        self._update_stats(0,0,0,0)
        rl.addWidget(stats_title); rl.addWidget(self.stats_text, 0)

        # Wire data options
        self.btn_export_csv.clicked.connect(self._export_csv)
        self.btn_export_xlsx.clicked.connect(self._export_xlsx)
        self.btn_copy.clicked.connect(self._copy_emails)
        self.btn_data_clear.clicked.connect(self._clear_emails)

        # Add to splitter
        splitter.addWidget(left)
        splitter.addWidget(mid)
        splitter.addWidget(right)
        splitter.setSizes([320, 900, 360])
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

        # Seed dropdowns (real rules/sites come in Step 5)
        if self.rule.count() == 0:
            self.rule.addItems(["Popular"])
        if self.site.count() == 0:
            self.site.addItem("Google", "https://www.google.com/")
            self.site.addItem("ScienceDirect", "https://www.sciencedirect.com/")
            self.site.addItem("SpringerLink", "https://link.springer.com/")
            self.site.addItem("Wiley", "https://onlinelibrary.wiley.com/")
            self.site.addItem("Taylor & Francis", "https://www.tandfonline.com/")
            self.site.addItem("PLOS ONE", "https://journals.plos.org/plosone/")
            self.site.addItem("SAGE Journals", "https://journals.sagepub.com/")
            self.site.addItem("Oxford Academic", "https://academic.oup.com/")
            self.site.addItem("Research Square", "https://www.researchsquare.com/")
            self.site.addItem("Hindawi", "https://www.hindawi.com/")
            self.site.addItem("Cureus", "https://www.cureus.com/")

    def _sep(self) -> QFrame:
        line = QFrame(); line.setFrameShape(QFrame.Shape.VLine); line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def _tool(self, text: str, tip: str, cb) -> QToolButton:
        b = QToolButton(); b.setText(text); b.setToolTip(tip); b.clicked.connect(cb); b.setAutoRaise(False)
        b.setFixedHeight(30)
        return b

    # ---------- NAV ----------
    def _navigate(self, url: str):
        q = to_qurl(url)
        self.web.setUrl(q)
        self.address.setText(q.toString())

    def _on_address_enter(self):
        self._navigate(self.address.text())

    def _on_home(self):
        self._navigate("https://www.google.com/")

    def _on_back(self):
        self.web.back()

    def _on_forward(self):
        self.web.forward()

    def _on_reload(self):
        self.web.reload()

    def _on_open_clicked(self):
        site_url = self.site.currentData() if self.site.currentData() else None
        target = site_url or self.address.text() or "https://www.google.com/"
        self._navigate(target)

    def _noop(self):
        # Placeholder for Step 5 wiring
        pass

    # ---------- LEFT PANEL ACTIONS ----------
    def _add_urls(self, urls):
        prefix = self.prefix_edit.text().strip()
        items = []
        for u in urls:
            u = (u or "").strip()
            if not u:
                continue
            if prefix and not u.startswith(prefix):
                u = prefix + u
            items.append(u)
        items = dedup_preserve_order(items)
        for u in items:
            self.url_list.addItem(QListWidgetItem(u))

    def _act_paste(self):
        text = QGuiApplication.clipboard().text() or ""
        # Paste smart: split by whitespace/newlines, treat as URLs
        parts = [p.strip() for p in text.replace("\r", "\n").split("\n") if p.strip()]
        if not parts and text:
            parts = [text.strip()]
        self._add_urls(parts)

    def _act_split(self):
        # Split current selected item (or clipboard) by lines into individual URLs
        if self.url_list.selectedItems():
            text = self.url_list.selectedItems()[0].text()
        else:
            text = QGuiApplication.clipboard().text() or ""
        parts = [p.strip() for p in text.replace("\r", "\n").split("\n") if p.strip()]
        self._add_urls(parts)

    def _act_dedup(self):
        items = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        self.url_list.clear()
        for u in dedup_preserve_order(items):
            self.url_list.addItem(u)

    def _act_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import URLs", "", "Text/CSV (*.txt *.csv);;All Files (*.*)")
        if not path:
            return
        urls = []
        try:
            if path.lower().endswith(".csv"):
                with open(path, newline="", encoding="utf-8") as f:
                    for row in csv.reader(f):
                        for cell in row:
                            cell = (cell or "").strip()
                            if cell:
                                urls.append(cell)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            urls.append(line)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))
            return
        self._add_urls(urls)

    def _save_queue(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save URL Queue", "url_queue.json", "JSON (*.json)")
        if not path:
            return
        data = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _load_queue(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load URL Queue", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.url_list.clear()
            for u in data:
                if isinstance(u, str) and u.strip():
                    self.url_list.addItem(u.strip())
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))

    def _select_prev(self):
        i = self.url_list.currentRow()
        if i <= 0:
            self.url_list.setCurrentRow(0)
        else:
            self.url_list.setCurrentRow(i - 1)

    def _select_next(self):
        i = self.url_list.currentRow()
        if i < 0:
            if self.url_list.count() > 0:
                self.url_list.setCurrentRow(0)
            return
        if i + 1 < self.url_list.count():
            self.url_list.setCurrentRow(i + 1)

    def _clear_queue(self):
        self.url_list.clear()

    # ---------- RIGHT PANEL ACTIONS ----------
    def _collect_email(self, email: str):
        # Helper for later steps; safe add now
        if not email:
            return
        # dedup
        existing = {self.data_view.item(i).text().lower() for i in range(self.data_view.count())}
        if email.lower() not in existing:
            self.data_view.addItem(email)

    def _clear_emails(self):
        self.data_view.clear()

    def _copy_emails(self):
        emails = [self.data_view.item(i).text() for i in range(self.data_view.count())]
        QGuiApplication.clipboard().setText("\n".join(emails))

    def _export_csv(self):
        if self.data_view.count() == 0:
            QMessageBox.information(self, "Export CSV", "No data to export.")
            return
        default = f"emails_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", default, "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["email"])
                for i in range(self.data_view.count()):
                    w.writerow([self.data_view.item(i).text()])
        except Exception as e:
            QMessageBox.critical(self, "Export CSV Error", str(e))

    def _export_xlsx(self):
        if self.data_view.count() == 0:
            QMessageBox.information(self, "Export Excel", "No data to export.")
            return
        default = f"emails_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", default, "Excel (*.xlsx)")
        if not path:
            return
        try:
            # Try to use openpyxl; fallback to CSV if unavailable
            try:
                from openpyxl import Workbook  # type: ignore
                wb = Workbook()
                ws = wb.active
                ws.title = "emails"
                ws.append(["email"])
                for i in range(self.data_view.count()):
                    ws.append([self.data_view.item(i).text()])
                wb.save(path)
            except Exception as ex:
                # Fallback: save CSV next to chosen path
                alt = os.path.splitext(path)[0] + ".csv"
                with open(alt, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["email"])
                    for i in range(self.data_view.count()):
                        w.writerow([self.data_view.item(i).text()])
                QMessageBox.information(self, "Export Fallback",
                    f"openpyxl missing or failed.\nSaved CSV instead:\n{alt}\n\nError: {ex}")
        except Exception as e:
            QMessageBox.critical(self, "Export Excel Error", str(e))

    # ---------- STATS ----------
    def _update_stats(self, data_today:int, data_session:int, pages_today:int, pages_session:int):
        self.stats_text.setPlainText(
            f"Data Collected\n  Today: {data_today}\n  Session: {data_session}\n\n"
            f"Pages Visited\n  Today: {pages_today}\n  Session: {pages_session}"
        )

    # ---------- STATE ----------
    def _restore_state(self):
        s = self._settings
        n_val = s.value("ui/n_spin", 50, type=int); self.n_spin.setValue(n_val)
        rule_idx = s.value("ui/rule_idx", -1, type=int)
        site_idx = s.value("ui/site_idx", -1, type=int)
        if 0 <= rule_idx < self.rule.count(): self.rule.setCurrentIndex(rule_idx)
        if 0 <= site_idx < self.site.count(): self.site.setCurrentIndex(site_idx)
        sizes = s.value("ui/splitter_sizes")
        if isinstance(sizes, list) and len(sizes) == 3:
            self.splitter.setSizes([int(x) for x in sizes])

    def closeEvent(self, event):
        s = self._settings
        s.setValue("ui/n_spin", self.n_spin.value())
        s.setValue("ui/rule_idx", self.rule.currentIndex())
        s.setValue("ui/site_idx", self.site.currentIndex())
        s.setValue("ui/splitter_sizes", self.splitter.sizes())
        super().closeEvent(event)
