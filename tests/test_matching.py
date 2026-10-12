from data_science_jobs.matching import parse_resume, rank_jobs
from data_science_jobs.matching.skill_match import compare_skills, extract_skills


def test_resume_parser_extracts_skills_and_experience() -> None:
    profile = parse_resume("Python, SQL, Tableau, pandas. 2 years of analytics experience in Boston.")
    assert {"Python", "SQL", "Tableau", "Pandas"} <= profile.skills
    assert profile.years_experience == 2
    assert "Boston" in profile.locations


def test_skill_comparison_returns_matched_and_missing() -> None:
    resume_skills = extract_skills("Python SQL Tableau")
    matched, missing, job_skills = compare_skills(resume_skills, "Data Analyst role using SQL, Python, dbt, and A/B testing.")
    assert matched == ["Python", "SQL"]
    assert "dbt" in missing
    assert "A/B Testing" in job_skills


def test_rank_jobs_prioritizes_skill_and_location_fit() -> None:
    profile = parse_resume("Python SQL pandas Tableau data quality ETL Boston")
    jobs = [
        {
            "company": "A",
            "title": "Senior Machine Learning Engineer",
            "location": "Berlin",
            "description": "PyTorch deep learning",
            "job_family": "Machine Learning / AI",
            "work_mode": "On-site / Location-based",
            "experience": "Senior / Manager",
            "visa": "Not specified",
        },
        {
            "company": "B",
            "title": "Data Analyst",
            "location": "Boston, MA",
            "description": "Use SQL, Python, Tableau, and data quality checks.",
            "job_family": "Data Analyst",
            "work_mode": "On-site / Location-based",
            "experience": "Entry / Associate",
            "visa": "Not specified",
        },
    ]
    ranked = rank_jobs(jobs, profile, prefer_boston_remote=True)
    assert ranked[0]["company"] == "B"
    assert ranked[0]["match_score"] > ranked[1]["match_score"]
    assert "SQL" in ranked[0]["matched_skills"]

