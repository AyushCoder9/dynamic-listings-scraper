from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from playwright.sync_api import Browser, BrowserContext, Playwright, sync_playwright


@contextmanager
def browser_context(headless: bool = True) -> Iterator[tuple[Playwright, Browser, BrowserContext]]:
    with sync_playwright() as playwright:
        # Prefer the full Chromium build (more likely to be present) and allow fallback
        # to the headless shell when available.
        browser = playwright.chromium.launch(headless=headless, channel="chromium")
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        try:
            yield playwright, browser, context
        finally:
            context.close()
            browser.close()
