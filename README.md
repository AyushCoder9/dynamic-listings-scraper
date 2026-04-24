# Dynamic Procurement Listings Scraper

Python + Playwright scraper for JavaScript-heavy procurement/tender listing pages.

This implementation targets **Option A (public procurement / tender website)** and is configured for **GeM India (bidplus.gem.gov.in)**. The scraper is config-driven so additional tender portals can be added by updating selectors in `config/sites.yaml`.

## Features

- Config-driven selectors (`config/sites.yaml`)
- Listing-page crawl with pagination and deduplicated detail links
- Detail-page enrichment with safe merge rules
- Retry/backoff for transient load issues
- Graceful handling of missing fields and per-record failures
- Data normalization (text, dates, budget)
- Export to both CSV and JSON in `output/`
- Run summary logs in `output/scraper.log`

## Project Layout

- `config/sites.yaml` site URLs and selectors
- `src/main.py` CLI entrypoint
- `src/scraper/` browser, listing, detail modules
- `src/parsers/normalize.py` field normalization helpers
- `src/io/exporter.py` CSV/JSON output
- `src/utils/` retry and logging utilities
- `writeup.md` short assignment note

## Setup

1. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Install browser binaries:
   - `python -m playwright install chromium`

## Configure Selectors

Sites are configured in `config/sites.yaml`. For this submission, the primary site key is `gem_india`.

To adapt the scraper to a different portal, add a new site entry and provide:

- `base_url`, `start_url`
- Listing selectors (`listing_item`, `title`, `detail_link`, etc.)
- Optional detail selectors (if the detail page has additional fields)
- Pagination selector (`pagination_next`)

## Run

- Headless (default):
  - `python -m src.main --site gem_india --max-pages 5`
- Headful (for debugging selectors):
  - `python -m src.main --site gem_india --max-pages 3 --headful`

## Output

- CSV: `output/tenders_<timestamp>.csv`
- JSON: `output/tenders_<timestamp>.json`
- Logs: `output/scraper.log`

For this submission, the most recent verified output is:

- `output/tenders_20260424_171105.json`
- `output/tenders_20260424_171105.csv`

## Notes and Limits

- The scraper only works while page structure remains consistent.
- Public site availability, temporary throttling, or policy changes can affect runs.
- Keep usage respectful and compliant with the site terms and local law.

## Data Notes (GeM)

- GeM listing cards do not expose a consistent “price/budget” field. The listing block we scrape contains **Quantity**, so the scraper stores this as `quantity` / `quantity_raw`.
- `price_or_budget` is populated **only when an explicit value is found** on the bid document (PDF). When no labeled value is present, it remains blank (`null`).

## Detail pages (GeM)

- On GeM, the “detail” link on the listing card commonly points to a **bid document** endpoint (`/showbidDocument/...`) which serves a PDF.
- This project treats that PDF as the detail source and performs **best-effort PDF text extraction** to enrich fields like `price_or_budget` (when labeled) and to validate dates/quantity.

## Suggested Improvements

- Add selector auto-validation tests
- Add periodic checkpoint files for very long runs
- Add scheduler integration for periodic updates
- Add richer schema and quality scoring for extracted records
