**Approach & tools used:** Python + Playwright. Selectors and start URLs are config-driven in `config/sites.yaml`. The scraper paginates GeM listing pages (`/all-bids`), extracts card fields, and deduplicates detail links. On GeM, the “detail” link commonly points to a bid-document PDF endpoint (`/showbidDocument/<id>`), so the scraper downloads the PDF and performs best‑effort text extraction (first pages) to enrich fields when explicit labels exist (e.g., “Bid Value”). Listing vs detail values are merged by precedence: prefer detail when present; otherwise keep listing values.

**Challenges faced:** GeM cards contain compact/messy blocks (items, department, dates) and do not reliably expose “price/budget” on the listing page; the detail source is often a PDF rather than HTML.

**How failures were handled:** robots.txt allow-check, randomized delays, and retry/backoff for transient failures. PDF enrichment is best-effort: per-record errors are captured and the crawl continues without aborting the run.

**What would break:** DOM/selector changes, pagination behavior changes, throttling/403 responses, or changes in PDF structure/text extraction quality.

**How I would improve it:** selector health checks, checkpoint/resume for long runs, richer PDF field extraction, and small regression tests for normalization and parsing.
