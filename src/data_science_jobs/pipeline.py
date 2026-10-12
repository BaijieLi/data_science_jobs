from __future__ import annotations

import logging
from typing import Any, Iterable

from .classification import (
    classify_domain,
    classify_experience,
    classify_role,
    classify_work_mode,
    is_graduate_friendly,
    should_keep_job,
)
from .schema import canonicalize_job
from .sources import fetch_all_sources, load_registry
from .validation import split_valid_jobs


LOGGER = logging.getLogger(__name__)


def enrich_job(row: dict[str, Any]) -> dict[str, Any] | None:
    title = row.get("title", "")
    description = row.get("description", "")
    if not should_keep_job(title, description):
        return None
    role = classify_role(title, description)
    experience = classify_experience(title, description)
    enriched = canonicalize_job(row)
    enriched["job_family"] = role
    enriched["experience"] = experience
    enriched["work_mode"] = classify_work_mode(title, row.get("location", ""), row)
    enriched["domain"] = classify_domain(title, description, row.get("source_focus", ""))
    enriched["graduate_friendly"] = is_graduate_friendly(experience)
    return enriched


def dedupe_jobs(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for row in rows:
        key = (
            row.get("application_url") or row.get("posting_url") or "",
            row.get("company", "").lower(),
            row.get("title", "").lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def build_job_board(sources: list[dict[str, str]] | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    raw_rows, errors = fetch_all_sources(sources or load_registry())
    enriched = [job for row in raw_rows if (job := enrich_job(row))]
    deduped = dedupe_jobs(enriched)
    valid, validation_errors = split_valid_jobs(deduped)
    if validation_errors:
        LOGGER.info("dropped %s invalid job rows", len(validation_errors))
    return valid, errors + validation_errors
