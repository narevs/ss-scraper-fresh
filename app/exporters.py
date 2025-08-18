"""Export helpers."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from PyQt6.QtWidgets import QApplication

from .storage import Record


def export_csv(records: Iterable[Record], path: str) -> str:
    path = str(Path(path))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            ["id", "email", "journal", "topic", "verified", "duplicate", "source_url", "timestamp_utc"],
        )
        writer.writeheader()
        for r in records:
            writer.writerow(r.__dict__)
    return path


def export_xlsx(records: Iterable[Record], path: str) -> str:
    path = str(Path(path))
    wb = Workbook()
    ws = wb.active
    headers = ["id", "email", "journal", "topic", "verified", "duplicate", "source_url", "timestamp_utc"]
    ws.append(headers)
    for r in records:
        ws.append([getattr(r, h) for h in headers])
    wb.save(path)
    return path


def copy_to_clipboard(records: Iterable[Record]) -> None:
    emails = "\n".join(r.email for r in records)
    QApplication.clipboard().setText(emails)
