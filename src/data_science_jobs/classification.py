from __future__ import annotations

import html
import re
from typing import Mapping


ROLE_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "Machine Learning / AI",
        (
            r"\bmachine learning\b",
            r"\bml engineer\b",
            r"\bai engineer\b",
            r"\bapplied scientist\b",
            r"\bresearch scientist\b",
            r"\bdeep learning\b",
            r"\bcomputer vision\b",
            r"\bnlp\b",
            r"\bllm\b",
            r"\bgenerative ai\b",
        ),
    ),
    (
        "Data Scientist",
        (
            r"\bdata scientist\b",
            r"\bdecision scientist\b",
            r"\bstatistician\b",
            r"\beconomist\b",
            r"\bquantitative researcher\b",
            r"\bquantitative analyst\b",
        ),
    ),
    (
        "Data Analyst",
        (
            r"\bdata analyst\b",
            r"\banalytics analyst\b",
            r"\bproduct analyst\b",
            r"\bbusiness analyst\b",
            r"\bgrowth analyst\b",
            r"\binsights analyst\b",
            r"\bmarketing analyst\b",
        ),
    ),
    (
        "Data Engineering",
        (
            r"\bdata engineer\b",
            r"\banalytics engineer\b",
            r"\betl\b",
            r"\bdata platform\b",
            r"\bdata infrastructure\b",
            r"\bwarehouse\b",
        ),
    ),
    (
        "Business Intelligence",
        (
            r"\bbusiness intelligence\b",
            r"\bbi analyst\b",
            r"\bbi engineer\b",
            r"\breporting analyst\b",
        ),
    ),
]

SENIOR_PATTERNS = (
    r"\bsenior\b",
    r"\bsr\.\b",
    r"\bstaff\b",
    r"\bprincipal\b",
    r"\blead\b",
    r"\bmanager\b",
    r"\bdirector\b",
    r"\bhead of\b",
    r"\bvp\b",
)

ENTRY_PATTERNS = (
    r"\bentry\b",
    r"\bjunior\b",
    r"\bassociate\b",
    r"\bapprentice\b",
    r"\brotation",
    r"\brotational\b",
    r"\b0-2 years\b",
    r"\b0 to 2 years\b",
    r"\b1\+ years\b",
)

NEW_GRAD_PATTERNS = (
    r"\bnew grad\b",
    r"\bnew graduate\b",
    r"\buniversity grad\b",
    r"\brecent graduate\b",
    r"\bearly career\b",
    r"\bcampus\b",
)

INTERN_PATTERNS = (
    r"\bintern\b",
    r"\binternship\b",
    r"\bco-op\b",
    r"\bstudent\b",
)

EXCLUDE_TITLE_PATTERNS = (
    r"\bdata center\b",
    r"\bdata centre\b",
    r"\bdatabase administrator\b",
    r"\bsolutions engineer\b",
    r"\bsolution engineer\b",
    r"\bsolutions architect\b",
    r"\bsolution architect\b",
    r"\bsales engineer\b",
    r"\baccount executive\b",
    r"\bcustomer success\b",
    r"\btechnical success\b",
    r"\bproduct manager\b",
    r"\bprogram manager\b",
    r"\bproject manager\b",
    r"\bmarketing manager\b",
    r"\brecruiter\b",
)

DATA_SOFTWARE_TITLE_PATTERNS = (
    r"\bsoftware engineer\b.*\b(data|analytics|machine learning|ml|ai|database|warehouse|query|infrastructure|platform)\b",
    r"\b(data|analytics|machine learning|ml|ai|database|warehouse|query)\b.*\bsoftware engineer\b",
)


def strip_html(value: str | None) -> str:
    if not value:
        return ""
    text = re.sub(r"<br\s*/?>", " ", value, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def classify_role(title: str, description: str = "") -> str:
    title_text = title.lower()
    if _contains_any(title_text, EXCLUDE_TITLE_PATTERNS):
        return "Other"
    for label, patterns in ROLE_RULES:
        if _contains_any(title_text, patterns):
            return label
    if _contains_any(title_text, DATA_SOFTWARE_TITLE_PATTERNS):
        if _contains_any(title_text, (r"\bmachine learning\b", r"\bml\b", r"\bai\b")):
            return "Machine Learning / AI"
        return "Data Engineering"
    return "Other"


def classify_experience(title: str, description: str = "") -> str:
    title_text = title.lower()
    if _contains_any(title_text, INTERN_PATTERNS):
        return "Internship"
    if _contains_any(title_text, NEW_GRAD_PATTERNS):
        return "New Grad"
    if _contains_any(title_text, SENIOR_PATTERNS):
        return "Senior / Manager"
    if _contains_any(title_text, ENTRY_PATTERNS):
        return "Entry / Associate"
    return "Professional / Unspecified"


def classify_work_mode(title: str, location: str, raw: Mapping[str, object] | None = None) -> str:
    raw = raw or {}
    workplace = str(raw.get("workplaceType") or raw.get("workplace_type") or "")
    is_remote = raw.get("isRemote")
    haystack = f"{title} {location} {workplace}".lower()
    if is_remote is True or "remote" in haystack:
        return "Remote"
    if "hybrid" in haystack:
        return "Hybrid"
    if any(term in haystack for term in ("office", "on-site", "onsite")):
        return "On-site"
    if location:
        return "On-site / Location-based"
    return "Unspecified"


def classify_domain(title: str, description: str, company_focus: str = "") -> str:
    haystack = f"{title} {description} {company_focus}".lower()
    if any(term in haystack for term in ("llm", "machine learning", "ai", "model", "research scientist")):
        return "AI / ML"
    if any(term in haystack for term in ("risk", "fraud", "credit", "finance", "payments", "banking", "fintech")):
        return "Finance / Risk"
    if any(term in haystack for term in ("health", "clinical", "bio", "medical")):
        return "Healthcare / Bio"
    if any(term in haystack for term in ("product analytics", "growth", "marketplace", "consumer")):
        return "Product Analytics"
    if any(term in haystack for term in ("data platform", "warehouse", "etl", "infrastructure", "pipeline")):
        return "Data Platform"
    if any(term in haystack for term in ("civic", "public-interest", "government", "justice")):
        return "Public Interest"
    return "General Data"


def is_graduate_friendly(experience: str) -> bool:
    return experience in {"Internship", "New Grad", "Entry / Associate", "Professional / Unspecified"}


def should_keep_job(title: str, description: str = "") -> bool:
    return classify_role(title, description) != "Other"
