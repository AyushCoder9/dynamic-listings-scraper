from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class TenderRecord:
    item_title: str | None = None
    organization_or_seller: str | None = None
    price_or_budget: str | None = None
    quantity: str | None = None
    category_or_department: str | None = None
    date_posted: str | None = None
    date_closing: str | None = None
    detail_page_link: str | None = None
    location: str | None = None
    tender_id_or_reference: str | None = None
    price_or_budget_raw: str | None = None
    quantity_raw: str | None = None
    date_posted_raw: str | None = None
    date_closing_raw: str | None = None
    source_site: str | None = None
    scraped_at_utc: str | None = None

    @classmethod
    def with_defaults(cls, **kwargs: Any) -> "TenderRecord":
        payload = dict(kwargs)
        payload.setdefault("scraped_at_utc", datetime.now(timezone.utc).isoformat())
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
