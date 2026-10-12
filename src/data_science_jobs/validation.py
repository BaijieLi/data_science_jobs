from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = ("title", "company", "location", "source", "apply_url")


def validate_job(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not str(row.get(field) or "").strip():
            errors.append(f"missing {field}")
    apply_url = str(row.get("apply_url") or "")
    if apply_url and not apply_url.startswith(("http://", "https://")):
        errors.append("apply_url is not an HTTP URL")
    return errors


def split_valid_jobs(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    valid: list[dict[str, Any]] = []
    errors: list[str] = []
    for row in rows:
        row_errors = validate_job(row)
        if row_errors:
            label = f"{row.get('company', 'Unknown')} - {row.get('title', 'Unknown')}"
            errors.append(f"{label}: {', '.join(row_errors)}")
            continue
        valid.append(row)
    return valid, errors

