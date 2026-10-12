from data_science_jobs.schema import canonicalize_job, first_salary_text, visa_signal
from data_science_jobs.validation import validate_job


def test_salary_and_visa_extraction() -> None:
    text = "The salary range is $80,000 - $110,000 per year. No visa sponsorship is available."
    assert first_salary_text(text).startswith("$80,000")
    assert "No sponsorship" in visa_signal(text)


def test_canonicalize_job_adds_common_fields() -> None:
    row = canonicalize_job(
        {
            "title": "Data Analyst",
            "company": "Example",
            "location": "Remote",
            "provider": "greenhouse",
            "application_url": "https://example.com/apply",
            "published_at": "2026-10-11",
            "description": "SQL and Python",
        }
    )
    assert row["source"] == "greenhouse"
    assert row["apply_url"] == "https://example.com/apply"
    assert row["posted_date"] == "2026-10-11"
    assert validate_job(row) == []


def test_validation_requires_apply_url() -> None:
    errors = validate_job({"title": "Data Analyst", "company": "Example", "location": "Boston", "source": "test"})
    assert "missing apply_url" in errors

