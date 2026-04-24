from __future__ import annotations

from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


def is_allowed_by_robots(start_url: str, user_agent: str = "assignment-scraper") -> tuple[bool, str]:
    parsed = urlparse(start_url)
    robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)
    try:
        parser.read()
        allowed = parser.can_fetch(user_agent, start_url)
        return allowed, robots_url
    except Exception:
        # If robots.txt cannot be fetched reliably, return unknown state and let caller decide.
        return True, robots_url
