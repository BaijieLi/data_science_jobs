from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from data_science_jobs.pipeline import build_job_board  # noqa: E402
from data_science_jobs.sources import load_registry  # noqa: E402


st.set_page_config(page_title="Data Science Jobs", page_icon="📊", layout="wide")


@st.cache_data(ttl=3600, show_spinner=False)
def load_jobs() -> tuple[pd.DataFrame, list[str]]:
    rows, errors = build_job_board()
    return pd.DataFrame(rows), errors


def safe_options(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    return sorted(value for value in df[column].dropna().unique() if value)


st.title("Data Science Graduate Job Board")
st.caption("Live company-posted roles for data science, analytics, ML, AI, and data engineering.")

with st.spinner("Refreshing live company job boards..."):
    jobs, errors = load_jobs()

source_count = len(load_registry())
if jobs.empty:
    st.error("No jobs were returned right now. Try refreshing in a few minutes.")
    if errors:
        with st.expander("Fetch errors"):
            st.write(errors)
    st.stop()

left, mid1, mid2, mid3, mid4 = st.columns(5)
left.metric("live roles", f"{len(jobs):,}")
mid1.metric("companies", f"{jobs['company'].nunique():,}")
mid2.metric("remote roles", f"{(jobs['work_mode'] == 'Remote').sum():,}")
mid3.metric("grad-friendly", f"{jobs['graduate_friendly'].sum():,}")
mid4.metric("sources checked", f"{source_count:,}")

with st.sidebar:
    st.header("Filters")
    search = st.text_input("Search title, company, location, domain")
    hide_senior = st.checkbox("Hide senior / manager roles", value=True)
    families = st.multiselect("Role category", safe_options(jobs, "job_family"))
    modes = st.multiselect("Work mode", safe_options(jobs, "work_mode"))
    experiences = st.multiselect("Experience level", safe_options(jobs, "experience"))
    domains = st.multiselect("Domain", safe_options(jobs, "domain"))
    companies = st.multiselect("Company", safe_options(jobs, "company"))

filtered = jobs.copy()
if hide_senior:
    filtered = filtered[filtered["experience"] != "Senior / Manager"]
if search:
    mask = pd.Series(False, index=filtered.index)
    for column in ("title", "company", "location", "domain", "job_family"):
        mask = mask | filtered[column].fillna("").str.contains(search, case=False, regex=False)
    filtered = filtered[mask]
if families:
    filtered = filtered[filtered["job_family"].isin(families)]
if modes:
    filtered = filtered[filtered["work_mode"].isin(modes)]
if experiences:
    filtered = filtered[filtered["experience"].isin(experiences)]
if domains:
    filtered = filtered[filtered["domain"].isin(domains)]
if companies:
    filtered = filtered[filtered["company"].isin(companies)]

st.subheader(f"{len(filtered):,} matching jobs")

display_columns = [
    "company",
    "title",
    "location",
    "work_mode",
    "experience",
    "job_family",
    "domain",
    "application_url",
]
st.dataframe(
    filtered[display_columns].rename(columns={"application_url": "apply"}),
    use_container_width=True,
    hide_index=True,
    column_config={
        "apply": st.column_config.LinkColumn("apply", display_text="Apply"),
    },
)

st.download_button(
    "Download filtered CSV",
    data=filtered[display_columns].to_csv(index=False).encode("utf-8"),
    file_name="data_science_jobs_filtered.csv",
    mime="text/csv",
)

if errors:
    with st.expander(f"{len(errors)} sources had temporary fetch errors"):
        st.write(errors)

