from __future__ import annotations

import re
from typing import Any


COMMON_SCHEMA = (
    "title",
    "company",
    "location",
    "salary",
    "description",
    "posted_date",
    "source",
    "apply_url",
)

SALARY_PATTERNS = (
    r"\$[0-9][0-9,]*(?:\s*-\s*\$?[0-9][0-9,]*)?(?:\s*(?:USD|/year|per year|annually))?",
    r"[0-9][0-9,]*\s*-\s*[0-9][0-9,]*\s*(?:USD|EUR|GBP|CAD|AUD)",
)

VISA_POSITIVE = (
    "visa sponsorship",
    "sponsor visas",
    "sponsorship available",
    "work authorization sponsorship",
)
VISA_NEGATIVE = (
    "does not sponsor",
    "do not sponsor",
    "no visa sponsorship",
    "without sponsorship",
    "must be authorized to work",
)


def first_salary_text(*values: object) -> str:
    for value in values:
        if not value:
            continue
        text = str(value)
        for pattern in SALARY_PATTERNS:
            match = re.search(pattern, text, flags=re.I)
            if match:
                return re.sub(r"\s+", " ", match.group(0)).strip()
    return ""


def format_ashby_compensation(compensation: Any) -> str:
    if not compensation:
        return ""
    if isinstance(compensation, dict):
        parts = []
        for key in ("compensationTierSummary", "summary", "description"):
            if compensation.get(key):
                parts.append(str(compensation[key]))
        if parts:
            return " | ".join(dict.fromkeys(parts))
    if isinstance(compensation, list):
        parts = [format_ashby_compensation(item) for item in compensation]
        return " | ".join(part for part in parts if part)
    return first_salary_text(compensation)


def format_recruitee_salary(salary: Any) -> str:
    if not isinstance(salary, dict):
        return ""
    low = salary.get("min")
    high = salary.get("max")
    currency = salary.get("currency") or ""
    period = salary.get("period") or ""
    if low and high:
        return f"{currency} {low}-{high} {period}".strip()
    if low:
        return f"{currency} {low}+ {period}".strip()
    return ""


def visa_signal(description: str) -> str:
    text = description.lower()
    if any(term in text for term in VISA_NEGATIVE):
        return "No sponsorship mentioned / likely requires authorization"
    if any(term in text for term in VISA_POSITIVE):
        return "Sponsorship mentioned"
    return "Not specified"


def canonicalize_job(row: dict[str, Any]) -> dict[str, Any]:
    description = str(row.get("description") or "")
    salary = str(row.get("salary") or "") or first_salary_text(description)
    canonical = dict(row)
    canonical["salary"] = salary
    canonical["source"] = row.get("provider") or row.get("source") or ""
    canonical["apply_url"] = row.get("application_url") or row.get("apply_url") or row.get("posting_url") or ""
    canonical["posted_date"] = row.get("published_at") or row.get("posted_date") or row.get("updated_at") or ""
    canonical["visa"] = row.get("visa") or visa_signal(description)
    return canonical

