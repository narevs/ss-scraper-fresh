"""Registry of supported publisher sites."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Site:
    label: str
    hosts: List[str]
    base_url: str
    search_url_template: str | None = None


SITES: List[Site] = [
    Site("ScienceDirect", ["sciencedirect.com"], "https://www.sciencedirect.com/"),
    Site("Springer", ["springer.com"], "https://link.springer.com/"),
    Site("Wiley", ["wiley.com"], "https://onlinelibrary.wiley.com/"),
    Site("Taylor & Francis", ["tandfonline.com"], "https://www.tandfonline.com/"),
    Site("PLOS ONE", ["plos.org"], "https://journals.plos.org/plosone/"),
    Site("SAGE Journals", ["sagepub.com"], "https://journals.sagepub.com/"),
    Site("Oxford Academic", ["oup.com", "academic.oup.com"], "https://academic.oup.com/"),
    Site("Research Square", ["researchsquare.com"], "https://www.researchsquare.com/"),
    Site("Hindawi", ["hindawi.com"], "https://www.hindawi.com/"),
    Site("ACS Publications", ["pubs.acs.org", "acs.org"], "https://pubs.acs.org/"),
    Site("Cureus", ["cureus.com"], "https://www.cureus.com/"),
]

SITE_MAP = {s.label: s for s in SITES}
