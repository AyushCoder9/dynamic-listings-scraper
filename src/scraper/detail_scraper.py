from __future__ import annotations

from playwright.sync_api import BrowserContext, Page

from src.models import TenderRecord
from src.utils.pdf_extract import download_pdf_bytes, extract_text_from_pdf, parse_fields_from_pdf_text
from src.utils.retry import retryable


class DetailScraper:
    def __init__(self, context: BrowserContext, site_config: dict, logger):
        self.context = context
        self.site_config = site_config
        self.logger = logger
        self.selectors = site_config["selectors"]
        self.delays = site_config.get("delays", {"min_seconds": 1.0, "max_seconds": 2.0})

    def _sleep(self) -> None:
        import random
        import time
        time.sleep(random.uniform(self.delays["min_seconds"], self.delays["max_seconds"]))

    def _safe_text(self, page: Page, selector: str | None) -> str | None:
        if not selector:
            return None
        try:
            # Using locator instead of query_selector to support pseudo-selectors like :has-text
            loc = page.locator(selector).first
            if loc.count() == 0:
                return None
            text = loc.inner_text().strip()
            return text or None
        except Exception:
            return None

    @retryable()
    def _goto(self, page: Page, url: str) -> None:
        page.goto(url, wait_until="networkidle", timeout=self.site_config.get("timeout_ms", 45000))

    def _is_download_url(self, url: str) -> bool:
        lowered = url.lower()
        download_markers = (
            "showbiddocument/",
            "showradocumentpdf/",
            ".pdf",
            "download",
        )
        return any(marker in lowered for marker in download_markers)

    def enrich(self, records: list[TenderRecord]) -> tuple[list[TenderRecord], list[dict]]:
        failures: list[dict] = []
        total = len([r for r in records if r.detail_page_link])
        with self.context.new_page() as page:
            processed = 0
            for record in records:
                if not record.detail_page_link:
                    continue
                processed += 1
                if processed == 1 or processed % 10 == 0:
                    self.logger.info("Detail enrichment progress: %s/%s", processed, total)
                try:
                    if self._is_download_url(record.detail_page_link):
                        self._enrich_from_pdf(record)
                    else:
                        self._goto(page, record.detail_page_link)
                        self._apply_merge(record, page)
                    self._sleep()
                except Exception as exc:  # noqa: BLE001
                    failure = {
                        "url": record.detail_page_link,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    }
                    failures.append(failure)
                    self.logger.warning("Detail extraction failed for %s: %s", record.detail_page_link, exc)
        return records, failures

    def _enrich_from_pdf(self, record: TenderRecord) -> None:
        # PDF parsing is best-effort: we avoid failing the run on extraction gaps.
        pdf_timeout = int(self.site_config.get("pdf_timeout_seconds", 20))
        pdf_bytes = download_pdf_bytes(record.detail_page_link, timeout_seconds=pdf_timeout)
        text = extract_text_from_pdf(pdf_bytes, max_pages=2)
        parsed = parse_fields_from_pdf_text(text)

        if parsed.tender_reference and not record.tender_id_or_reference:
            record.tender_id_or_reference = parsed.tender_reference
        if parsed.quantity and not record.quantity:
            record.quantity = parsed.quantity
            record.quantity_raw = record.quantity_raw or f"Quantity: {parsed.quantity}"
        if parsed.date_posted_raw and not record.date_posted_raw:
            record.date_posted_raw = parsed.date_posted_raw
            record.date_posted = parsed.date_posted_raw
        if parsed.date_closing_raw and not record.date_closing_raw:
            record.date_closing_raw = parsed.date_closing_raw
            record.date_closing = parsed.date_closing_raw

        # Only set price/budget if we found an explicit value label
        if parsed.price_or_budget_raw and not record.price_or_budget_raw:
            record.price_or_budget_raw = parsed.price_or_budget_raw
            record.price_or_budget = parsed.price_or_budget_raw

    def _pick(self, detail_value: str | None, listing_value: str | None) -> str | None:
        return detail_value if detail_value else listing_value

    def _apply_merge(self, record: TenderRecord, page: Page) -> None:
        detail_title = self._safe_text(page, self.selectors.get("detail_title"))
        if detail_title and detail_title.lower().startswith("403"):
            detail_title = None
        detail_org = self._safe_text(page, self.selectors.get("detail_organization"))
        detail_price = self._safe_text(page, self.selectors.get("detail_price"))
        detail_category = self._safe_text(page, self.selectors.get("detail_category"))
        detail_posted = self._safe_text(page, self.selectors.get("detail_date_posted"))
        detail_closing = self._safe_text(page, self.selectors.get("detail_date_closing"))
        detail_location = self._safe_text(page, self.selectors.get("detail_location"))
        detail_reference = self._safe_text(page, self.selectors.get("detail_tender_reference"))

        record.item_title = self._pick(detail_title, record.item_title)
        record.organization_or_seller = self._pick(detail_org, record.organization_or_seller)
        record.price_or_budget = self._pick(detail_price, record.price_or_budget)
        record.price_or_budget_raw = self._pick(detail_price, record.price_or_budget_raw)
        # Quantity is generally a listing-card attribute on GeM; keep listing value unless a site provides it on detail.
        record.quantity = self._pick(self._safe_text(page, self.selectors.get("detail_quantity")), record.quantity)
        record.quantity_raw = self._pick(self._safe_text(page, self.selectors.get("detail_quantity")), record.quantity_raw)
        record.category_or_department = self._pick(detail_category, record.category_or_department)
        record.date_posted = self._pick(detail_posted, record.date_posted)
        record.date_posted_raw = self._pick(detail_posted, record.date_posted_raw)
        record.date_closing = self._pick(detail_closing, record.date_closing)
        record.date_closing_raw = self._pick(detail_closing, record.date_closing_raw)
        record.location = self._pick(detail_location, record.location)
        record.tender_id_or_reference = self._pick(detail_reference, record.tender_id_or_reference)
