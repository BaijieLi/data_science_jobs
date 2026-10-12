from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import requests

from .classification import strip_html


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "source_registry.json"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (data-science-jobs portfolio project)",
}


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> list[dict[str, str]]:
    with Path(path).open() as f:
        return json.load(f)


def source_url(source: dict[str, str]) -> str:
    provider = source["provider"]
    board = source["board"]
    if provider == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    if provider == "lever":
        return f"https://api.lever.co/v0/postings/{board}?mode=json"
    if provider == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true"
    raise ValueError(f"Unsupported provider: {provider}")


def fetch_json(source: dict[str, str], timeout: int = 20) -> Any:
    response = requests.get(source_url(source), headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


def normalize_greenhouse(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    departments = job.get("departments") or []
    department = ", ".join(d.get("name", "") for d in departments if d.get("name"))
    return {
        "job_id": str(job.get("id") or job.get("internal_job_id") or ""),
        "company": job.get("company_name") or source["company"],
        "title": job.get("title") or "",
        "location": (job.get("location") or {}).get("name") or "",
        "department": department,
        "employment_type": "",
        "posting_url": job.get("absolute_url") or "",
        "application_url": job.get("absolute_url") or "",
        "published_at": job.get("first_published") or "",
        "updated_at": job.get("updated_at") or "",
        "description": strip_html(job.get("content")),
        "raw_workplace": "",
        "provider": "greenhouse",
        "source_focus": source.get("focus", ""),
    }


def normalize_lever(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    categories = job.get("categories") or {}
    lists = " ".join(strip_html(item.get("content", "")) for item in job.get("lists", []))
    description = " ".join(
        part
        for part in (
            job.get("descriptionPlain") or strip_html(job.get("description")),
            lists,
        )
        if part
    )
    return {
        "job_id": str(job.get("id") or ""),
        "company": source["company"],
        "title": job.get("text") or "",
        "location": categories.get("location") or "",
        "department": categories.get("team") or "",
        "employment_type": categories.get("commitment") or "",
        "posting_url": job.get("hostedUrl") or "",
        "application_url": job.get("applyUrl") or job.get("hostedUrl") or "",
        "published_at": "",
        "updated_at": str(job.get("createdAt") or ""),
        "description": description,
        "raw_workplace": job.get("workplaceType") or "",
        "provider": "lever",
        "source_focus": source.get("focus", ""),
    }


def normalize_ashby(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    secondary = job.get("secondaryLocations") or []
    extra_locations = [loc.get("location", "") for loc in secondary if isinstance(loc, dict)]
    locations = [job.get("location") or ""] + [loc for loc in extra_locations if loc]
    return {
        "job_id": str(job.get("id") or ""),
        "company": source["company"],
        "title": job.get("title") or "",
        "location": "; ".join(dict.fromkeys(locations)),
        "department": job.get("department") or job.get("team") or "",
        "employment_type": job.get("employmentType") or "",
        "posting_url": job.get("jobUrl") or "",
        "application_url": job.get("applyUrl") or job.get("jobUrl") or "",
        "published_at": job.get("publishedAt") or "",
        "updated_at": "",
        "description": job.get("descriptionPlain") or strip_html(job.get("descriptionHtml")),
        "raw_workplace": job.get("workplaceType") or "",
        "provider": "ashby",
        "source_focus": source.get("focus", ""),
        "isRemote": job.get("isRemote"),
    }


def normalize_jobs(payload: Any, source: dict[str, str]) -> list[dict[str, Any]]:
    provider = source["provider"]
    if provider == "greenhouse":
        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        return [normalize_greenhouse(job, source) for job in jobs]
    if provider == "lever":
        jobs = payload if isinstance(payload, list) else []
        return [normalize_lever(job, source) for job in jobs]
    if provider == "ashby":
        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        return [normalize_ashby(job, source) for job in jobs if job.get("isListed", True)]
    return []


def fetch_source(source: dict[str, str], timeout: int = 20) -> tuple[list[dict[str, Any]], str | None]:
    try:
        payload = fetch_json(source, timeout=timeout)
        return normalize_jobs(payload, source), None
    except Exception as exc:  # keep the live app useful even if one company rate-limits.
        return [], f"{source['company']}: {exc}"


def fetch_all_sources(
    sources: Iterable[dict[str, str]] | None = None,
    max_workers: int = 16,
    timeout: int = 20,
) -> tuple[list[dict[str, Any]], list[str]]:
    sources = list(sources or load_registry())
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_source, source, timeout): source for source in sources}
        for future in as_completed(futures):
            result, error = future.result()
            rows.extend(result)
            if error:
                errors.append(error)
    return rows, errors

