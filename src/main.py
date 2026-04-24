from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.io.exporter import export_records
from src.parsers.normalize import normalize_records
from src.scraper.browser import browser_context
from src.scraper.detail_scraper import DetailScraper
from src.scraper.listing_scraper import ListingScraper
from src.utils.logging import configure_logger
from src.utils.robots import is_allowed_by_robots


def load_site_config(config_path: str, site_key: str) -> dict:
    with Path(config_path).open("r", encoding="utf-8") as handle:
        all_sites = yaml.safe_load(handle)
    if site_key not in all_sites["sites"]:
        raise KeyError(f"Unknown site key '{site_key}'. Available: {', '.join(all_sites['sites'].keys())}")
    return all_sites["sites"][site_key]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dynamic procurement listing scraper")
    parser.add_argument("--site", default="gem_india", help="Site key from config/sites.yaml (e.g., gem_india)")
    parser.add_argument("--config", default="config/sites.yaml", help="Path to YAML site config")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum listing pages to visit")
    parser.add_argument("--headful", action="store_true", help="Run browser in non-headless mode")
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    logger = configure_logger("procurement_scraper")
    site = load_site_config(args.config, args.site)
    allowed, robots_url = is_allowed_by_robots(site["start_url"])
    if not allowed:
        raise PermissionError(f"Scraping blocked by robots.txt policy at {robots_url}")
    logger.info("robots.txt check passed: %s", robots_url)

    with browser_context(headless=not args.headful) as (_, _, context):
        listing_scraper = ListingScraper(context=context, site_config=site, logger=logger)
        detail_scraper = DetailScraper(context=context, site_config=site, logger=logger)

        listing_records, discovered_links, pages_visited = listing_scraper.crawl(max_pages=args.max_pages)
        enriched_records, failures = detail_scraper.enrich(listing_records)
        normalized = normalize_records(enriched_records)
        csv_path, json_path = export_records(normalized)

    logger.info("Run complete")
    logger.info("Pages visited: %s", pages_visited)
    logger.info("Unique detail links discovered: %s", len(discovered_links))
    logger.info("Records extracted: %s", len(normalized))
    logger.info("Failed detail URLs: %s", len(failures))
    if failures:
        for failure in failures:
            logger.warning(
                "Detail failure | %s | %s | %s",
                failure["error_type"],
                failure["url"],
                failure["message"],
            )
    logger.info("CSV output: %s", csv_path)
    logger.info("JSON output: %s", json_path)


if __name__ == "__main__":
    run()
