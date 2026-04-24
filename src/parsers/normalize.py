from __future__ import annotations

import re

from dateutil import parser as date_parser

from src.models import TenderRecord


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    # Strip common GeM labels
    labels = ["Items:", "Quantity:", "Department Name And Address:", "Start Date:", "End Date:", "Bid No.:"]
    for label in labels:
        if value.startswith(label):
            value = value[len(label):].strip()
    
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def _normalize_date(value: str | None) -> str | None:
    value = _clean_text(value)
    if not value:
        return None
    try:
        dt = date_parser.parse(value, fuzzy=True)
        return dt.date().isoformat()
    except Exception:  # noqa: BLE001
        return value


def _normalize_budget(value: str | None) -> str | None:
    value = _clean_text(value)
    if not value:
        return None

    numeric_fragments = re.findall(r"\d[\d,]*(?:\.\d+)?", value)
    if not numeric_fragments:
        return value

    normalized_parts = [part.replace(",", "") for part in numeric_fragments]
    if len(normalized_parts) == 1:
        return normalized_parts[0]
    return " - ".join(normalized_parts)


def _normalize_quantity(value: str | None) -> str | None:
    value = _clean_text(value)
    if not value:
        return None
    match = re.search(r"Quantity:\s*([\d,]+)", value, flags=re.IGNORECASE)
    if match:
        return match.group(1).replace(",", "")
    # Fallback: if the field is just a number-like string
    numeric_fragments = re.findall(r"\d[\d,]*", value)
    if len(numeric_fragments) == 1:
        return numeric_fragments[0].replace(",", "")
    return None


def _extract_location(org_string: str | None) -> str | None:
    if not org_string:
        return None
    # Common Indian States/UTs/Cities for GeM location enrichment
    locations = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
        "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
        "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
        "Uttarakhand", "West Bengal", "Delhi", "New Delhi", "Chandigarh", "Ladakh", "Jammu and Kashmir",
        "Mumbai", "Kolkata", "Chennai", "Bengaluru", "Hyderabad", "Pune", "Ahmedabad", "Visakhapatnam"
    ]
    org_lower = org_string.lower()
    for loc in locations:
        if loc.lower() in org_lower:
            return loc
    
    # Fallback for Central Ministries (most are in New Delhi)
    if "ministry of" in org_lower:
        return "New Delhi (Central Govt)"
    
    return "India"


def _infer_category(item_title: str | None) -> str | None:
    if not item_title:
        return "Unclassified"
    service_keywords = ["service", "manpower", "maintenance", "consultancy", "amc", "cmc", "hiring"]
    if any(kw in item_title.lower() for kw in service_keywords):
        return "Service"
    return "Product"


def normalize_records(records: list[TenderRecord]) -> list[TenderRecord]:
    for record in records:
        record.item_title = _clean_text(record.item_title)
        record.organization_or_seller = _clean_text(record.organization_or_seller)
        
        # GeM Specific Enrichment
        if record.source_site == "GeM India (Government e-Marketplace)":
            if not record.location:
                record.location = _extract_location(record.organization_or_seller)
            if not record.category_or_department:
                record.category_or_department = _infer_category(record.item_title)

        record.category_or_department = _clean_text(record.category_or_department)
        record.location = _clean_text(record.location)
        
        if record.tender_id_or_reference:
            ref = _clean_text(record.tender_id_or_reference)
            if ref and "Notice identifier:" in ref:
                ref = ref.split("Notice identifier:")[-1].strip()
            record.tender_id_or_reference = ref

        record.price_or_budget_raw = _clean_text(record.price_or_budget_raw)
        record.price_or_budget = _normalize_budget(record.price_or_budget)

        record.quantity_raw = _clean_text(record.quantity_raw)
        record.quantity = _normalize_quantity(record.quantity)

        record.date_posted_raw = _clean_text(record.date_posted_raw)
        record.date_posted = _normalize_date(record.date_posted)
        record.date_closing_raw = _clean_text(record.date_closing_raw)
        record.date_closing = _normalize_date(record.date_closing)

    return records
