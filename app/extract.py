"""Email extraction utilities."""
from __future__ import annotations

import re
from typing import Iterable, List

from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}")


def _dedup(emails: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for e in emails:
        e = e.lower()
        if e not in seen:
            seen.add(e)
            result.append(e)
    return result


def extract_emails_from_html(html: str) -> List[str]:
    """Extract emails giving precedence to ``mailto:`` links."""
    soup = BeautifulSoup(html, "html.parser")
    emails: List[str] = []
    # 1. mailto links
    for tag in soup.select("a[href^=mailto]"):
        addr = tag.get("href", "")[7:]
        addr = addr.split("?")[0]
        if EMAIL_REGEX.fullmatch(addr):
            emails.append(addr)
    # 2. visible text
    text = soup.get_text(" ")
    for match in EMAIL_REGEX.finditer(text):
        emails.append(match.group(0))
    return _dedup(emails)


# Placeholder functions for broader architecture

def extract_emails_from_view(view) -> List[str]:  # pragma: no cover - GUI integration
    return []


def extract_emails_from_assets(view) -> List[str]:  # pragma: no cover - attachments
    return []


def ocr_if_enabled(*args, **kwargs) -> List[str]:  # pragma: no cover - OCR
    return []


def mx_verify_async(emails: Iterable[str], on_result=None) -> None:  # pragma: no cover - MX
    return None
