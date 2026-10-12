from __future__ import annotations

from typing import Any

from .resume_parser import ResumeProfile
from .skill_match import compare_skills


ROLE_WEIGHTS = {
    "Data Analyst": 1.0,
    "Data Engineering": 0.95,
    "Data Scientist": 0.92,
    "Business Intelligence": 0.88,
    "Machine Learning / AI": 0.78,
}


def location_score(location: str, work_mode: str, prefer_boston_remote: bool = True) -> float:
    if not prefer_boston_remote:
        return 0.75
    text = f"{location} {work_mode}".lower()
    if "remote" in text:
        return 1.0
    if any(term in text for term in ("boston", "cambridge", "massachusetts", " ma", "ma,", "ma ")):
        return 1.0
    if "united states" in text or "us" in text:
        return 0.65
    if not location:
        return 0.5
    return 0.25


def experience_score(experience: str) -> float:
    return {
        "Internship": 0.9,
        "New Grad": 1.0,
        "Entry / Associate": 1.0,
        "Professional / Unspecified": 0.78,
        "Senior / Manager": 0.35,
    }.get(experience, 0.6)


def visa_score(visa: str, needs_sponsorship: bool = False) -> float:
    if not needs_sponsorship:
        return 0.75
    text = visa.lower()
    if "sponsorship mentioned" in text:
        return 1.0
    if "no sponsorship" in text or "requires authorization" in text:
        return 0.15
    return 0.45


def score_job(
    job: dict[str, Any],
    resume: ResumeProfile,
    prefer_boston_remote: bool = True,
    needs_sponsorship: bool = False,
) -> dict[str, Any]:
    job_text = " ".join(str(job.get(field, "")) for field in ("title", "description", "job_family", "domain"))
    matched, missing, job_skills = compare_skills(resume.skills, job_text)
    skill_score = len(matched) / len(job_skills) if job_skills else 0.45
    role_score = ROLE_WEIGHTS.get(str(job.get("job_family") or ""), 0.55)
    loc_score = location_score(str(job.get("location") or ""), str(job.get("work_mode") or ""), prefer_boston_remote)
    exp_score = experience_score(str(job.get("experience") or ""))
    v_score = visa_score(str(job.get("visa") or ""), needs_sponsorship)

    score = (
        skill_score * 45
        + role_score * 20
        + loc_score * 18
        + exp_score * 12
        + v_score * 5
    )
    ranked = dict(job)
    ranked["match_score"] = round(score, 1)
    ranked["matched_skills"] = ", ".join(matched)
    ranked["missing_skills"] = ", ".join(missing[:10])
    ranked["job_skills"] = ", ".join(job_skills)
    return ranked


def rank_jobs(
    jobs: list[dict[str, Any]],
    resume: ResumeProfile,
    prefer_boston_remote: bool = True,
    needs_sponsorship: bool = False,
) -> list[dict[str, Any]]:
    ranked = [
        score_job(
            job,
            resume,
            prefer_boston_remote=prefer_boston_remote,
            needs_sponsorship=needs_sponsorship,
        )
        for job in jobs
    ]
    return sorted(ranked, key=lambda row: float(row.get("match_score") or 0), reverse=True)

