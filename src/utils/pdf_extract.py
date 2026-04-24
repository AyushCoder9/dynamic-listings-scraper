from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Optional
from urllib.request import Request, urlopen

from pypdf import PdfReader

from src.utils.retry import retryable


@dataclass
class ExtractedPdfFields:
    title: Optional[str] = None
    tender_reference: Optional[str] = None
    organization: Optional[str] = None
    quantity: Optional[str] = None
    date_posted_raw: Optional[str] = None
    date_closing_raw: Optional[str] = None
    price_or_budget_raw: Optional[str] = None


@retryable(attempts=2)
def download_pdf_bytes(url: str, timeout_seconds: int = 20) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    with urlopen(req, timeout=timeout_seconds) as resp:  # noqa: S310
        return resp.read()


def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 2) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    texts: list[str] = []
    for i, page in enumerate(reader.pages):
        if i >= max_pages:
            break
        page_text = page.extract_text() or ""
        texts.append(page_text)
    return "\n".join(texts)


def parse_fields_from_pdf_text(text: str) -> ExtractedPdfFields:
    # Make matching easier
    flat = re.sub(r"\s+", " ", text).strip()

    # Tender reference patterns commonly seen on tender PDFs
    tender_reference = None
    m = re.search(r"\bGEM/\d{4}/[BR]/\d+\b", flat, flags=re.IGNORECASE)
    if m:
        tender_reference = m.group(0).upper()

    # Quantity
    quantity = None
    m = re.search(r"\bQuantity\b\s*[:\-]?\s*([\d,]+)\b", flat, flags=re.IGNORECASE)
    if m:
        quantity = m.group(1).replace(",", "")

    # Dates (best-effort; keep raw)
    date_posted_raw = None
    m = re.search(r"\bStart Date\b\s*[:\-]?\s*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4}[^\\n]{0,25})", flat, flags=re.IGNORECASE)
    if m:
        date_posted_raw = m.group(1).strip()

    date_closing_raw = None
    m = re.search(r"\bEnd Date\b\s*[:\-]?\s*([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4}[^\\n]{0,25})", flat, flags=re.IGNORECASE)
    if m:
        date_closing_raw = m.group(1).strip()

    # Budget/value (very portal-specific; keep raw fragment if found)
    price_or_budget_raw = None
    m = re.search(
        r"\b(Estimated Value|Bid Value|Tender Value|Total Value)\b\s*[:\-]?\s*(INR|Rs\\.?|₹)?\s*([\d,]+(?:\\.[0-9]+)?)",
        flat,
        flags=re.IGNORECASE,
    )
    if m:
        price_or_budget_raw = f"{m.group(1)}: {(m.group(2) or '')}{m.group(3)}".strip()

    # Title (first non-empty line-ish)
    title = None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        # avoid extremely generic headers if present
        title = lines[0][:200]

    return ExtractedPdfFields(
        title=title,
        tender_reference=tender_reference,
        organization=None,
        quantity=quantity,
        date_posted_raw=date_posted_raw,
        date_closing_raw=date_closing_raw,
        price_or_budget_raw=price_or_budget_raw,
    )

