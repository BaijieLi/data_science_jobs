from __future__ import annotations

from dataclasses import dataclass
import re

from .skill_match import extract_skills


@dataclass(frozen=True)
class ResumeProfile:
    raw_text: str
    skills: set[str]
    years_experience: float
    locations: set[str]


LOCATION_PATTERNS = {
    "Boston": r"\bboston\b|\bcambridge\b|\bmassachusetts\b|\bma\b",
    "Remote": r"\bremote\b",
    "New York": r"\bnew york\b|\bnyc\b",
    "San Francisco": r"\bsan francisco\b|\bbay area\b",
}


def estimate_years_experience(text: str) -> float:
    values = [float(match.group(1)) for match in re.finditer(r"\b(\d+(?:\.\d+)?)\+?\s+years?", text, flags=re.I)]
    if values:
        return max(values)
    return 0.0


def extract_locations(text: str) -> set[str]:
    found = set()
    for label, pattern in LOCATION_PATTERNS.items():
        if re.search(pattern, text, flags=re.I):
            found.add(label)
    return found


def parse_resume(text: str) -> ResumeProfile:
    text = text or ""
    return ResumeProfile(
        raw_text=text,
        skills=extract_skills(text),
        years_experience=estimate_years_experience(text),
        locations=extract_locations(text),
    )

