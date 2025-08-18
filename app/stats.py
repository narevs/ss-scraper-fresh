"""Session and daily statistics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class Counters:
    emails_today: int = 0
    emails_session: int = 0
    pages_today: int = 0
    pages_session: int = 0
    _last: date = date.today()

    def _rollover(self) -> None:
        today = date.today()
        if today != self._last:
            self.emails_today = 0
            self.pages_today = 0
            self._last = today

    def inc_emails(self, n: int) -> None:
        self._rollover()
        self.emails_today += n
        self.emails_session += n

    def inc_pages(self) -> None:
        self._rollover()
        self.pages_today += 1
        self.pages_session += 1


counters = Counters()
