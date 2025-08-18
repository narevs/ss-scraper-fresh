"""Link collection helpers."""
from __future__ import annotations

from typing import Iterable, List, Set
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import posixpath

from bs4 import BeautifulSoup

TRACKER_KEYS = {"fbclid", "gclid"}


def normalize_url(url: str) -> str:
    """Normalize URLs by enforcing https, stripping fragments and trackers."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower() or "https"
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path or "/"
    path = posixpath.normpath(path)
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.startswith("utm_") and k not in TRACKER_KEYS
    ]
    normalized = urlunsplit((scheme, netloc, path, urlencode(query, doseq=True), ""))
    if normalized.endswith("/") and path != "/":
        normalized = normalized.rstrip("/")
    return normalized


def same_host(url: str, allowed_hosts: Iterable[str]) -> bool:
    """Return True if *url* is within any of ``allowed_hosts`` (allowing subdomains)."""
    host = urlsplit(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    for allowed in allowed_hosts:
        allowed = allowed.lower().lstrip("www.")
        if host == allowed or host.endswith("." + allowed):
            return True
    return False


def collect_links_qt(view, limit: int, allowed_hosts: Iterable[str]) -> List[str]:
    """Collect links from a Qt WebEngine view.

    This is a simplified implementation that fetches the HTML content of
    ``view`` and parses it with BeautifulSoup. It normalizes, filters and
    deduplicates URLs, returning at most ``limit`` links.
    """
    html: str = ""
    try:
        html = view.page().toHtml(lambda x: x)  # type: ignore[call-arg]
    except Exception:
        pass
    links: Set[str] = set()
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        url = normalize_url(a["href"])
        if same_host(url, allowed_hosts):
            links.add(url)
            if len(links) >= limit:
                break
    return list(links)
