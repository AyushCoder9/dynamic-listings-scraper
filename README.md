# 🛡️ Procurement Intelligence Scraper (GeM India)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/engine-playwright-green.svg)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, production-grade web scraper specifically engineered for the **Government e-Marketplace (GeM) India** portal. Designed for the **GemEdge** internship application, this tool demonstrates advanced handling of JavaScript-heavy dynamic content, automated data normalization, and intelligent metadata inference.

---

## 🎯 Why GeM India?

For this assignment, I chose to scrape **GeM (bidplus.gem.gov.in)** because it represents the "Gold Standard" of procurement complexity in India:
*   **Dynamic DOM**: All bid cards are rendered via heavy JavaScript, requiring real-browser automation rather than simple HTTP requests.
*   **Technical Challenge**: Unlike standard tender portals, GeM detail links point directly to **PDF documents**. My scraper overcomes this by maximizing data extraction from listing cards and using intelligent fallbacks.
*   **Strategic Relevance**: As an applicant for **GemEdge**, implementing a robust GeM scraper directly showcases my ability to solve the core technical challenges your company handles daily.

---

## 🚀 Quick Start

### 1. Prerequisites
*   Python 3.9 or higher
*   pip (Python package manager)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/AyushCoder9/dynamic-listings-scraper.git
cd dynamic-listings-scraper

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Execution
```bash
# Run the GeM India scraper (Default: 1 page)
python -m src.main --site gem_india --max-pages 1

# Run with headful browser to watch the scraping process
python -m src.main --site gem_india --max-pages 1 --headful
```

---

## 🏗️ Project Architecture

The project follows a modular, configuration-driven design:

```text
├── config/
│   └── sites.yaml          # Centralized selectors and URL configurations
├── src/
│   ├── main.py             # CLI entrypoint and orchestrator
│   ├── models.py           # Data schemas (TenderRecord dataclass)
│   ├── scraper/
│   │   ├── browser.py      # Playwright browser & context initialization
│   │   ├── listing_scraper.py # Core logic for listing cards & pagination
│   │   └── detail_scraper.py  # Advanced detail page/document handling
│   ├── parsers/
│   │   └── normalize.py    # Data cleaning, date parsing & location inference
│   ├── io/
│   │   └── exporter.py     # CSV and JSON output generation
│   └── utils/              # Logging, retries, and robots.txt compliance
├── output/                 # Scraped data (JSON/CSV) and logs
└── writeup.md              # Technical design notes
```

### Key Logic Flow:
1.  **Discovery**: `ListingScraper` navigates to the "All Bids" page and identifies all bid cards.
2.  **Extraction**: For each card, it surgical-extracts data using refined CSS/XPath selectors.
3.  **Enrichment**:
    *   **Location**: Infers the Indian State/UT from the Department address.
    *   **Category**: Uses keyword analysis to classify bids as "Product" or "Service".
    *   **Dates**: Automatically converts various Indian date formats to standard **ISO 8601**.
4.  **Persistence**: Records are deduplicated and saved to timestamped CSV and JSON files in the `output/` directory.

---

## 📊 Sample Output

The scraper generates high-density procurement data. You can find sample results from my latest run here:
*   📂 **[Sample JSON Result](output/tenders_20260424_171105.json)**
*   📂 **[Sample CSV Result](output/tenders_20260424_171105.csv)**

---

## 🛡️ Engineering Best Practices
*   **Compliance**: Strictly respects `robots.txt` and implements randomized human-like delays.
*   **Resilience**: Built-in retry logic for network instability and graceful handling of missing fields.
*   **Observability**: Detailed execution logs are saved to `output/scraper.log`.
*   **Maintainability**: Adding a new site is as simple as adding 10 lines of YAML to `config/sites.yaml`.

---

**Developed for GemEdge Internship Application**
