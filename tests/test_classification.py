from data_science_jobs.classification import (
    classify_experience,
    classify_role,
    classify_work_mode,
    should_keep_job,
)


def test_classifies_core_data_roles() -> None:
    assert classify_role("Data Scientist, Product Analytics") == "Data Scientist"
    assert classify_role("Machine Learning Engineer, Recommendations") == "Machine Learning / AI"
    assert classify_role("Analytics Engineer") == "Data Engineering"
    assert classify_role("Business Intelligence Analyst") == "Business Intelligence"


def test_excludes_unrelated_data_center_titles() -> None:
    assert not should_keep_job("Data Center Facilities Technician")


def test_experience_labels_graduate_friendly_roles() -> None:
    assert classify_experience("Data Science Intern") == "Internship"
    assert classify_experience("New Grad Machine Learning Engineer") == "New Grad"
    assert classify_experience("Associate Data Analyst") == "Entry / Associate"
    assert classify_experience("Senior Data Scientist") == "Senior / Manager"


def test_work_mode_detection() -> None:
    assert classify_work_mode("Data Analyst", "Remote - United States") == "Remote"
    assert classify_work_mode("ML Engineer", "New York, NY Hybrid") == "Hybrid"
    assert classify_work_mode("Data Scientist", "San Francisco, CA") == "On-site / Location-based"

