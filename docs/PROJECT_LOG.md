## Project log (for maintainers)

This document captures key decisions, known issues, and next steps so a new developer can quickly continue work.

### Scope chosen

- Implemented **Option A** using a public procurement/tender portal.
- Current primary target: **GeM India (bidplus.gem.gov.in)**.

### How the scraper works (high level)

- **Config-driven**: sites are defined in `config/sites.yaml` (URLs + selectors).
- **Listing crawl** (`src/scraper/listing_scraper.py`):
  - Visits the start URL.
  - Extracts one record per card.
  - Collects and deduplicates detail links.
  - Moves across pages using `pagination_next`.
- **Detail enrichment** (`src/scraper/detail_scraper.py`):
  - Visits each discovered detail link (skips obvious download/PDF endpoints).
  - Merges fields using: “use detail value if present, otherwise keep listing value”.
- **Normalization + export**:
  - `src/parsers/normalize.py` cleans text, parses dates to ISO, normalizes numeric fragments.
  - `src/io/exporter.py` writes timestamped CSV/JSON into `output/`.
  - `output/scraper.log` captures a run summary.

### Practical issues encountered (and mitigation)

- **JavaScript-rendered pages**: used Playwright with `networkidle` waits and locator-based extraction.
- **Inconsistent “price/budget” availability on GeM listing cards**:
  - Current `selectors.price` points at the “Quantity” block (see `config/sites.yaml` under `gem_india`).
  - As a result, `price_or_budget` often reflects the extracted quantity, and `price_or_budget_raw` preserves the original listing block text.
- **PDF-based detail pages on GeM**:
  - The listing’s “detail” link commonly points to `/showbidDocument/...` which serves a PDF.
  - Detail enrichment uses best-effort **PDF text extraction** to capture labeled values (e.g., “Bid Value”) and validate dates/quantity.
- **Transient failures / throttling**:
  - Navigation is wrapped with retry/backoff.
  - Failures are recorded per record and the run continues.

### Known gaps

- **Budget vs quantity**: `price_or_budget` is not a reliable budget for GeM in its current configuration.
- **Detail selectors for GeM**: detail extraction is intentionally conservative; most GeM data is captured from listing cards.

### Next steps (recommended)

- Add a dedicated `quantity` field to the schema and map GeM “Quantity” into it.
- Update `price_or_budget` extraction for portals that expose an actual “Value/Estimated value/Award amount” field.
- Add a small selector validation check that fails fast when key selectors return no matches for multiple pages.
- Add a checkpoint/resume option for longer crawls.

