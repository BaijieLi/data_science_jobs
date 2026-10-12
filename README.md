# Data Science Jobs

A live job board for data science graduates looking for internships, new-grad roles, entry-level jobs, and professional data roles across remote, hybrid, and on-site work.

The app focuses on direct company application links. Instead of sending users through generic search results, it pulls public postings from company applicant tracking systems and classifies them into practical job-search categories.

## What It Does

- Aggregates live jobs from public Greenhouse and Ashby company boards.
- Filters for Data Scientist, Data Analyst, Machine Learning / AI, Data Engineering, and Business Intelligence roles.
- Classifies work mode as Remote, Hybrid, On-site / Location-based, or Unspecified.
- Labels experience level as Internship, New Grad, Entry / Associate, Professional / Unspecified, or Senior / Manager.
- Keeps direct `Apply` links to the original company posting.
- Lets users filter and download a CSV from the Streamlit interface.

## Run Locally

```bash
cd /Users/libaijie/Downloads/Github_project/data_science_jobs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_live_jobs.py
streamlit run app/streamlit_app.py
```

## Deploy on Streamlit

Use `app/streamlit_app.py` as the main file path. No API keys or secrets are required for the current public job sources.

## Project Structure

```text
app/                    Streamlit dashboard
data/source_registry.json
docs/                   Project notes and deployment guide
scripts/                Batch fetch/export scripts
src/data_science_jobs/  Source adapters, classification, pipeline
tests/                  Unit tests
```

## Portfolio Angle

This project shows an end-to-end data product: live data ingestion, normalization across multiple APIs, heuristic classification, user-facing filtering, CSV export, tests, and deployment-ready documentation.

