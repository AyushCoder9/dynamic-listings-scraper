from __future__ import annotations

import random
import time
from urllib.parse import urljoin

from playwright.sync_api import BrowserContext, Page

from src.models import TenderRecord
from src.utils.retry import retryable


class ListingScraper:
    def __init__(self, context: BrowserContext, site_config: dict, logger):
        self.context = context
        self.site_config = site_config
        self.logger = logger
        self.selectors = site_config["selectors"]
        self.delays = site_config.get("delays", {"min_seconds": 1.0, "max_seconds": 2.0})

    def _sleep(self) -> None:
        time.sleep(random.uniform(self.delays["min_seconds"], self.delays["max_seconds"]))

    @retryable()
    def _goto(self, page: Page, url: str) -> None:
        page.goto(url, wait_until="networkidle", timeout=self.site_config.get("timeout_ms", 45000))

    def _text(self, element, selector: str | None) -> str | None:
        if not selector:
            return None
        try:
            loc = element.locator(selector).first
            if loc.count() == 0:
                return None
            text = loc.inner_text().strip()
            return text or None
        except Exception:
            return None

    def crawl(self, max_pages: int) -> tuple[list[TenderRecord], set[str], int]:
        records: list[TenderRecord] = []
        seen_links: set[str] = set()
        pages_visited = 0
        stagnant_pages = 0

        with self.context.new_page() as page:
            current_url = self.site_config["start_url"]
            while current_url and pages_visited < max_pages:
                before_count = len(seen_links)
                pages_visited += 1
                self.logger.info("Visiting listing page %s: %s", pages_visited, current_url)
                self._goto(page, current_url)

                # Use locators for items and wait for at least one to be visible
                items_locator = page.locator(self.selectors["listing_item"])
                try:
                    items_locator.first.wait_for(timeout=15000, state="attached")
                except Exception:
                    self.logger.warning("No items found on page %s after timeout", pages_visited)
                
                count = items_locator.count()
                self.logger.info("Found %s listing elements on page %s", count, pages_visited)

                for i in range(count):
                    item = items_locator.nth(i)
                    
                    # Extract detail link first
                    href_node = item.locator(self.selectors["detail_link"]).first
                    if href_node.count() == 0:
                        self.logger.warning("Item %s: No detail link found with selector %s", i, self.selectors["detail_link"])
                        continue

                    href = href_node.get_attribute("href")
                    if not href:
                        self.logger.warning("Item %s: Href attribute missing", i)
                        continue

                    detail_url = urljoin(self.site_config["base_url"], href)
                    if detail_url in seen_links:
                        continue
                    seen_links.add(detail_url)

                    extracted_price_block = self._text(item, self.selectors.get("price"))
                    is_gem = self.site_config.get("name") == "GeM India (Government e-Marketplace)"
                    record = TenderRecord.with_defaults(
                        item_title=self._text(item, self.selectors.get("title")),
                        organization_or_seller=self._text(item, self.selectors.get("organization")),
                        # GeM listing cards commonly expose "Quantity" but not a reliable price/budget.
                        price_or_budget=None if is_gem else extracted_price_block,
                        price_or_budget_raw=None if is_gem else extracted_price_block,
                        quantity=extracted_price_block if is_gem else None,
                        quantity_raw=extracted_price_block if is_gem else None,
                        category_or_department=self._text(item, self.selectors.get("category")),
                        date_posted=self._text(item, self.selectors.get("date_posted")),
                        date_posted_raw=self._text(item, self.selectors.get("date_posted")),
                        date_closing=self._text(item, self.selectors.get("date_closing")),
                        date_closing_raw=self._text(item, self.selectors.get("date_closing")),
                        tender_id_or_reference=self._text(item, self.selectors.get("tender_id")),
                        detail_page_link=detail_url,
                        source_site=self.site_config["name"],
                    )
                    records.append(record)

                added_this_page = len(seen_links) - before_count
                if added_this_page == 0:
                    stagnant_pages += 1
                else:
                    stagnant_pages = 0

                next_url = None
                next_selector = self.selectors.get("pagination_next")
                if next_selector:
                    next_button = page.locator(next_selector).first
                    if next_button.count() > 0:
                        href = next_button.get_attribute("href")
                        if href and not href.startswith("#"):
                            next_url = urljoin(self.site_config["base_url"], href)
                        else:
                            next_button.click(timeout=8000)
                            page.wait_for_timeout(1200)
                            page.wait_for_load_state("networkidle")
                            next_url = page.url
                            # Hash/ajax pagination often keeps same URL; keep loop progress bounded by max_pages.
                            if next_url == current_url:
                                next_url = current_url

                if stagnant_pages >= 2:
                    self.logger.info("No new links for two consecutive pages; stopping crawl early.")
                    break

                current_url = next_url
                self._sleep()

        return records, seen_links, pages_visited
