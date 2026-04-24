# GemEdge
**B2G Procurement Intelligence for MSMEs**

**DATA SCRAPING ASSIGNMENT**
**REAL-WORLD CHALLENGE. REAL-WORLD IMPACT.**

---

## 1. OBJECTIVE
At GemEdge, we build data intelligence solutions for MSMEs to discover and win government procurement opportunities.

This assignment is designed to evaluate your ability to solve real-world data extraction problems involving dynamic websites, pagination, and messy data.

## 2. THE TASK
Build a scraper to extract structured data from a dynamic listings website.

**Choose ONE of the following:**
* **Option A:** Scrape data from any public procurement / tender website (e.g., State/PSU/International tender portals)
* **Option B:** Scrape data from a JS-heavy listings website (e.g., product directory, supplier directory, startup listings, etc.)

**DATA TO EXTRACT**
From listing pages and detail pages, extract the following fields (or closest equivalents if names differ):
* Item / Tender Title
* Organization / Seller
* Price / Budget (if available)
* Category / Department
* Date (Posted / Closing)
* Detail Page Link

*Note: You may add any other relevant fields that you believe will add value.*

## 3. REQUIREMENTS
* Handle pagination (at least 2–3 pages).
* Work with dynamic content (JavaScript-rendered pages).
* Extract data from both listing pages and detail pages.
* Output the final data in CSV or JSON format.
* Write clean, modular, and well-documented code.
* Handle missing data, errors, and inconsistencies gracefully.

## 4. SUBMISSION GUIDELINES
Submit the following to:
gopal@gemedge.dev

**Deadline:**
25/04/2026 9:00 PM

* Source code (GitHub repository link or ZIP file)
* Output dataset (CSV or JSON file)
* A short write-up (Max 300 words) covering:
    * Your approach and tools used
    * Challenges faced
    * How you handled failures
    * What would break in your scraper
    * How you would improve it

## 5. TECHNICAL GUIDELINES
* You may use Python (preferred) or any other language.
* Use tools/libraries like Selenium, Playwright, Requests, BeautifulSoup, etc.
* Respect robots.txt and website terms.
* Do not perform actions that can harm or overload the target website.
* Add delays and be considerate to avoid getting blocked.

## 6. IMPORTANT NOTES
* Do NOT manually copy or paste data.
* Do NOT submit without working code.
* Submissions that appear automated or lack originality will be rejected.
* We value problem-solving, code quality, and thinking over just the final output.

## 7. ANTI-CHEATING POLICY
We use multiple methods to verify the authenticity of submissions. Any form of plagiarsim, copied code, or use of automated scraping services will lead to immediate disqualification.

## 8. BONUS (HIGHLY VALUED)
* Handle pagination beyond 3 pages
* Implement retry logic / error handling
* Clean and normalize data
* Use config files / modular structure
* Avoid detection / blocking smartly

## 9. EVALUATION RUBRIC (Total: 20 Marks)

| Criteria | Description | Marks |
| :--- | :--- | :--- |
| **Functionality & Completeness** | Scraper works end-to-end, handles pagination and extracts all required fields | 0 - 5 |
| **Data Quality** | Data is accurate, consistent, properly structured, and well-cleaned | 0 - 4 |
| **Technical Approach** | Efficient use of tools/libraries, selectors strategy, code modularity | 0 - 4 |
| **Robustness & Error Handling** | Handles edge cases, missing data, failures, and continues execution | 0 - 4 |
| **Documentation & Explanation** | Clarity of approach, write-up quality, understanding of challenges | 0 - 3 |
| | **TOTAL** | **/ 20** |

---

**Build solutions that empower MSMES. | Your work drives real impact. | We can't wait to see what you build!**