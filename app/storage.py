"""In-memory storage for collected records."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List
from uuid import uuid4


@dataclass
class Record:
    id: str
    email: str
    journal: str = ""
    topic: str | None = None
    verified: str = "unknown"  # "true", "false" or "unknown"
    duplicate: bool = False
    source_url: str = ""
    timestamp_utc: str = ""


class Store:
    """Simple global-deduping storage."""

    def __init__(self) -> None:
        self.records: List[Record] = []
        self._seen: set[str] = set()

    def add_records(self, emails: Iterable[str], meta: Dict[str, str] | None = None) -> List[Record]:
        meta = meta or {}
        added: List[Record] = []
        for email in emails:
            duplicate = email in self._seen
            if not duplicate:
                self._seen.add(email)
            rec = Record(
                id=str(uuid4()),
                email=email,
                journal=meta.get("journal", ""),
                topic=meta.get("topic"),
                verified="unknown",
                duplicate=duplicate,
                source_url=meta.get("source_url", ""),
                timestamp_utc=datetime.now(timezone.utc).isoformat(),
            )
            self.records.append(rec)
            if not duplicate:
                added.append(rec)
        return added

    def clear(self) -> None:
        self.records.clear()
        self._seen.clear()


store = Store()
