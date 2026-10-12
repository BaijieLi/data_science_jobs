from data_science_jobs.sources import (
    normalize_ashby,
    normalize_greenhouse,
    normalize_rippling,
    normalize_smartrecruiters,
    normalize_workable,
    normalize_workday,
    source_url,
)


def test_greenhouse_normalizer_keeps_company_apply_link() -> None:
    source = {"company": "Example", "provider": "greenhouse", "board": "example", "focus": "Data"}
    job = {
        "id": 1,
        "company_name": "Example Co",
        "title": "Data Analyst",
        "location": {"name": "Remote"},
        "absolute_url": "https://example.com/jobs/1",
        "content": "<p>Analyze product metrics.</p>",
        "departments": [{"name": "Data"}],
    }
    row = normalize_greenhouse(job, source)
    assert row["company"] == "Example Co"
    assert row["application_url"] == "https://example.com/jobs/1"
    assert row["department"] == "Data"


def test_ashby_normalizer_prefers_apply_url() -> None:
    source = {"company": "Example", "provider": "ashby", "board": "example", "focus": "AI"}
    job = {
        "id": "abc",
        "title": "Machine Learning Engineer",
        "location": "Remote",
        "department": "Engineering",
        "jobUrl": "https://jobs.ashbyhq.com/example/abc",
        "applyUrl": "https://jobs.ashbyhq.com/example/abc/application",
        "descriptionPlain": "Build ML systems.",
    }
    row = normalize_ashby(job, source)
    assert row["application_url"].endswith("/application")
    assert row["posting_url"].endswith("/abc")


def test_source_url_builder() -> None:
    assert "greenhouse" in source_url({"provider": "greenhouse", "board": "stripe"})
    assert "lever.co" in source_url({"provider": "lever", "board": "example"})
    assert "ashbyhq" in source_url({"provider": "ashby", "board": "openai"})
    assert "workable" in source_url({"provider": "workable", "board": "example"})
    assert "smartrecruiters" in source_url({"provider": "smartrecruiters", "board": "Example"})


def test_workday_normalizer_builds_original_link() -> None:
    source = {
        "company": "Adobe",
        "provider": "workday",
        "board": "adobe/external",
        "board_url": "https://adobe.wd5.myworkdayjobs.com/external",
        "focus": "Creative software",
    }
    row = normalize_workday(
        {
            "title": "Data Scientist",
            "externalPath": "/job/San-Jose/Data-Scientist_R123",
            "locationsText": "San Jose",
            "postedOn": "Posted 1 Day Ago",
            "bulletFields": ["R123"],
        },
        source,
    )
    assert row["application_url"] == "https://adobe.wd5.myworkdayjobs.com/external/job/San-Jose/Data-Scientist_R123"
    assert row["provider"] == "workday"


def test_workable_rippling_and_smartrecruiters_normalizers() -> None:
    workable = normalize_workable(
        {
            "title": "Data Engineer",
            "shortcode": "ABC",
            "application_url": "https://apply.workable.com/j/ABC/apply",
            "url": "https://apply.workable.com/j/ABC",
            "telecommuting": True,
            "locations": [{"city": "London", "country": "United Kingdom"}],
        },
        {"company": "Example", "provider": "workable", "board": "example", "focus": "Data"},
    )
    assert workable["isRemote"] is True
    assert workable["application_url"].endswith("/apply")

    rippling = normalize_rippling(
        {
            "uuid": "uuid",
            "name": "Analytics Engineer",
            "url": "https://ats.rippling.com/example/jobs/uuid",
            "department": {"label": "Data"},
            "workLocation": {"label": "Remote (United States)"},
        },
        {"company": "Example", "provider": "rippling", "board": "example", "focus": "Data"},
    )
    assert rippling["department"] == "Data"

    smart = normalize_smartrecruiters(
        {
            "id": "123",
            "name": "Machine Learning Engineer",
            "company": {"name": "Example"},
            "location": {"fullLocation": "Berlin, Germany", "hybrid": True},
            "function": {"label": "Engineering"},
            "typeOfEmployment": {"label": "Full-time"},
        },
        {"company": "Example", "provider": "smartrecruiters", "board": "Example", "focus": "Data"},
    )
    assert smart["application_url"].startswith("https://jobs.smartrecruiters.com/Example/123-")
    assert smart["raw_workplace"] == "Hybrid"
