from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import requests

from .classification import strip_html
from .schema import first_salary_text, format_ashby_compensation, format_recruitee_salary


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "source_registry.json"
LOGGER = logging.getLogger(__name__)
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (data-science-jobs portfolio project)",
}
SEARCH_TERMS = ("data", "machine learning", "analytics", "AI")


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> list[dict[str, str]]:
    with Path(path).open() as f:
        return json.load(f)


def source_url(source: dict[str, str]) -> str:
    provider = source["provider"]
    board = source["board"]
    if source.get("api_url"):
        return source["api_url"]
    if provider == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    if provider == "lever":
        return f"https://api.lever.co/v0/postings/{board}?mode=json"
    if provider == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true"
    if provider == "workable":
        return f"https://apply.workable.com/api/v1/widget/accounts/{board}"
    if provider == "recruitee":
        return f"https://{board}.recruitee.com/api/offers/"
    if provider == "personio":
        return f"https://{board}.jobs.personio.de/xml"
    if provider == "rippling":
        return f"https://api.rippling.com/platform/api/ats/v1/board/{board}/jobs"
    if provider == "smartrecruiters":
        return f"https://api.smartrecruiters.com/v1/companies/{board}/postings?limit=100"
    raise ValueError(f"Unsupported provider: {provider}")


def fetch_json(source: dict[str, str], timeout: int = 20) -> Any:
    response = requests.get(source_url(source), headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


def search_terms(source: dict[str, str]) -> tuple[str, ...]:
    terms = source.get("search_terms")
    if isinstance(terms, list):
        return tuple(str(term) for term in terms)
    return SEARCH_TERMS


def normalize_greenhouse(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    departments = job.get("departments") or []
    department = ", ".join(d.get("name", "") for d in departments if d.get("name"))
    description = strip_html(job.get("content"))
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
        "salary": first_salary_text(description),
        "description": description,
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
        "salary": first_salary_text(description),
        "description": description,
        "raw_workplace": job.get("workplaceType") or "",
        "provider": "lever",
        "source_focus": source.get("focus", ""),
    }


def normalize_ashby(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    secondary = job.get("secondaryLocations") or []
    extra_locations = [loc.get("location", "") for loc in secondary if isinstance(loc, dict)]
    locations = [job.get("location") or ""] + [loc for loc in extra_locations if loc]
    description = job.get("descriptionPlain") or strip_html(job.get("descriptionHtml"))
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
        "salary": format_ashby_compensation(job.get("compensation")) or first_salary_text(description),
        "description": description,
        "raw_workplace": job.get("workplaceType") or "",
        "provider": "ashby",
        "source_focus": source.get("focus", ""),
        "isRemote": job.get("isRemote"),
    }


def normalize_workday(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    board_url = source.get("board_url") or ""
    external_path = job.get("externalPath") or ""
    posting_url = f"{board_url}{external_path}" if board_url and external_path else board_url
    return {
        "job_id": str(job.get("id") or job.get("bulletFields", [""])[0] or external_path),
        "company": source["company"],
        "title": job.get("title") or "",
        "location": job.get("locationsText") or "",
        "department": "",
        "employment_type": "",
        "posting_url": posting_url,
        "application_url": posting_url,
        "published_at": job.get("postedOn") or "",
        "updated_at": "",
        "salary": "",
        "description": "",
        "raw_workplace": "",
        "provider": "workday",
        "source_focus": source.get("focus", ""),
    }


def normalize_workable(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    locations = job.get("locations") or []
    location = "; ".join(
        ", ".join(part for part in (loc.get("city"), loc.get("region"), loc.get("country")) if part)
        for loc in locations
        if isinstance(loc, dict)
    )
    location = location or ", ".join(part for part in (job.get("city"), job.get("state"), job.get("country")) if part)
    description = strip_html(job.get("description"))
    return {
        "job_id": str(job.get("shortcode") or job.get("code") or ""),
        "company": source["company"],
        "title": job.get("title") or "",
        "location": location,
        "department": job.get("department") or "",
        "employment_type": job.get("employment_type") or "",
        "posting_url": job.get("url") or job.get("shortlink") or "",
        "application_url": job.get("application_url") or job.get("url") or "",
        "published_at": job.get("published_on") or job.get("created_at") or "",
        "updated_at": "",
        "salary": first_salary_text(description),
        "description": description,
        "raw_workplace": "Remote" if job.get("telecommuting") else "",
        "provider": "workable",
        "source_focus": source.get("focus", ""),
        "isRemote": job.get("telecommuting"),
    }


def normalize_recruitee(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    description = strip_html(job.get("description") or job.get("sharing_description"))
    return {
        "job_id": str(job.get("id") or job.get("guid") or ""),
        "company": job.get("company_name") or source["company"],
        "title": job.get("title") or "",
        "location": job.get("location") or ", ".join(part for part in (job.get("city"), job.get("country")) if part),
        "department": job.get("department") or "",
        "employment_type": job.get("employment_type_code") or "",
        "posting_url": job.get("careers_url") or "",
        "application_url": job.get("careers_apply_url") or job.get("careers_url") or "",
        "published_at": job.get("published_at") or job.get("created_at") or "",
        "updated_at": job.get("updated_at") or "",
        "salary": format_recruitee_salary(job.get("salary")) or first_salary_text(description),
        "description": description,
        "raw_workplace": "Remote" if job.get("remote") else ("Hybrid" if job.get("hybrid") else ""),
        "provider": "recruitee",
        "source_focus": source.get("focus", ""),
        "isRemote": job.get("remote"),
    }


def _xml_text(node: ET.Element, path: str) -> str:
    found = node.find(path)
    return (found.text or "").strip() if found is not None else ""


def normalize_personio(position: ET.Element, source: dict[str, str]) -> dict[str, Any]:
    job_id = _xml_text(position, "id")
    office = _xml_text(position, "office")
    additional = [
        (node.text or "").strip()
        for node in position.findall("./additionalOffices/office")
        if (node.text or "").strip()
    ]
    descriptions = [
        _xml_text(node, "value")
        for node in position.findall("./jobDescriptions/jobDescription")
    ]
    board_url = source.get("board_url") or f"https://{source['board']}.jobs.personio.de"
    posting_url = f"{board_url}/job/{job_id}" if job_id else board_url
    return {
        "job_id": job_id,
        "company": _xml_text(position, "subcompany") or source["company"],
        "title": _xml_text(position, "name"),
        "location": "; ".join([office, *additional]).strip("; "),
        "department": _xml_text(position, "department"),
        "employment_type": _xml_text(position, "employmentType"),
        "posting_url": posting_url,
        "application_url": posting_url,
        "published_at": "",
        "updated_at": "",
        "salary": first_salary_text(" ".join(descriptions)),
        "description": strip_html(" ".join(descriptions)),
        "raw_workplace": "",
        "provider": "personio",
        "source_focus": source.get("focus", ""),
    }


def normalize_rippling(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    department = job.get("department") or {}
    work_location = job.get("workLocation") or {}
    return {
        "job_id": str(job.get("uuid") or ""),
        "company": source["company"],
        "title": job.get("name") or "",
        "location": work_location.get("label") or "",
        "department": department.get("label") or department.get("id") or "",
        "employment_type": "",
        "posting_url": job.get("url") or "",
        "application_url": job.get("url") or "",
        "published_at": "",
        "updated_at": "",
        "salary": "",
        "description": "",
        "raw_workplace": work_location.get("label") or "",
        "provider": "rippling",
        "source_focus": source.get("focus", ""),
    }


def _slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "job"


def normalize_smartrecruiters(job: dict[str, Any], source: dict[str, str]) -> dict[str, Any]:
    location = job.get("location") or {}
    company = job.get("company") or {}
    function = job.get("function") or {}
    employment = job.get("typeOfEmployment") or {}
    experience = job.get("experienceLevel") or {}
    board = source["board"]
    title = job.get("name") or ""
    job_id = str(job.get("id") or "")
    posting_url = f"https://jobs.smartrecruiters.com/{board}/{job_id}-{_slugify(title)}" if job_id else ""
    return {
        "job_id": job_id,
        "company": company.get("name") or source["company"],
        "title": title,
        "location": location.get("fullLocation") or ", ".join(
            part for part in (location.get("city"), location.get("region"), location.get("country")) if part
        ),
        "department": function.get("label") or "",
        "employment_type": employment.get("label") or "",
        "posting_url": posting_url,
        "application_url": posting_url,
        "published_at": job.get("releasedDate") or "",
        "updated_at": "",
        "salary": "",
        "description": experience.get("label") or "",
        "raw_workplace": "Remote" if location.get("remote") else ("Hybrid" if location.get("hybrid") else ""),
        "provider": "smartrecruiters",
        "source_focus": source.get("focus", ""),
        "isRemote": location.get("remote"),
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
    if provider == "workable":
        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        return [normalize_workable(job, source) for job in jobs]
    if provider == "recruitee":
        jobs = payload.get("offers", []) if isinstance(payload, dict) else []
        return [normalize_recruitee(job, source) for job in jobs]
    if provider == "rippling":
        jobs = payload if isinstance(payload, list) else []
        return [normalize_rippling(job, source) for job in jobs]
    return []


def fetch_workday(source: dict[str, str], timeout: int = 20) -> list[dict[str, Any]]:
    url = source_url(source)
    rows: list[dict[str, Any]] = []
    for term in search_terms(source):
        try:
            response = requests.post(
                url,
                headers={**HEADERS, "Content-Type": "application/json"},
                json={"appliedFacets": {}, "limit": int(source.get("limit", 50)), "offset": 0, "searchText": term},
                timeout=timeout,
            )
            response.raise_for_status()
        except requests.RequestException:
            continue
        rows.extend(normalize_workday(job, source) for job in response.json().get("jobPostings", []))
    return rows


def fetch_personio(source: dict[str, str], timeout: int = 20) -> list[dict[str, Any]]:
    response = requests.get(source_url(source), headers={"User-Agent": HEADERS["User-Agent"]}, timeout=timeout)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    return [normalize_personio(position, source) for position in root.findall("./position")]


def fetch_smartrecruiters(source: dict[str, str], timeout: int = 20) -> list[dict[str, Any]]:
    base = f"https://api.smartrecruiters.com/v1/companies/{source['board']}/postings"
    rows: list[dict[str, Any]] = []
    for term in search_terms(source):
        try:
            response = requests.get(
                base,
                headers=HEADERS,
                params={"limit": int(source.get("limit", 100)), "offset": 0, "q": term},
                timeout=timeout,
            )
            response.raise_for_status()
        except requests.RequestException:
            continue
        rows.extend(normalize_smartrecruiters(job, source) for job in response.json().get("content", []))
    return rows


def fetch_source(source: dict[str, str], timeout: int = 20) -> tuple[list[dict[str, Any]], str | None]:
    try:
        if source["provider"] == "workday":
            return fetch_workday(source, timeout=timeout), None
        if source["provider"] == "personio":
            return fetch_personio(source, timeout=timeout), None
        if source["provider"] == "smartrecruiters":
            return fetch_smartrecruiters(source, timeout=timeout), None
        payload = fetch_json(source, timeout=timeout)
        return normalize_jobs(payload, source), None
    except Exception as exc:  # keep the live app useful even if one company rate-limits.
        LOGGER.warning("failed to fetch source %s: %s", source.get("company"), exc)
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
