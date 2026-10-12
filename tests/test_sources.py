from data_science_jobs.sources import normalize_ashby, normalize_greenhouse, source_url


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

