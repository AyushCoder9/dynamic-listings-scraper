from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.models import TenderRecord


def export_records(records: list[TenderRecord], output_dir: str = "output") -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    payload = [record.to_dict() for record in records if record.item_title and record.detail_page_link]
    columns = list(TenderRecord().to_dict().keys())
    csv_file = output_path / f"tenders_{timestamp}.csv"
    json_file = output_path / f"tenders_{timestamp}.json"

    df = pd.DataFrame(payload, columns=columns)
    if not df.empty:
        df = df.sort_values(by=["item_title"], kind="stable")
    df.to_csv(csv_file, index=False)

    with json_file.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    return csv_file, json_file
