import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


OUTPUT_FILE = Path(__file__).with_name("output.json")
_OUTPUT_LOCK = Lock()


def save_output(query: str, response: dict[str, Any]) -> dict[str, Any]:
    """
    Append one prompt result to the output JSON file and return the saved record.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "response": response,
    }

    with _OUTPUT_LOCK:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        records = _read_records()
        records.append(record)
        OUTPUT_FILE.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return record


def _read_records() -> list[dict[str, Any]]:
    if not OUTPUT_FILE.exists():
        return []

    try:
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup_file = OUTPUT_FILE.with_suffix(".invalid.json")
        OUTPUT_FILE.replace(backup_file)
        return []

    if isinstance(data, list):
        return data

    backup_file = OUTPUT_FILE.with_suffix(".invalid.json")
    OUTPUT_FILE.replace(backup_file)
    return []
