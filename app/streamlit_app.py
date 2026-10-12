from __future__ import annotations

from collections import Counter
from io import BytesIO
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from data_science_jobs.matching import parse_resume, rank_jobs  # noqa: E402
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


def read_uploaded_resume(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    data = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""
    if name.endswith(".docx"):
        try:
            from docx import Document

            doc = Document(BytesIO(data))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception:
            return ""
    return data.decode("utf-8", errors="ignore")


def boston_remote_mask(df: pd.DataFrame) -> pd.Series:
    text = (
        df["location"].fillna("")
        + " "
        + df["work_mode"].fillna("")
    ).str.lower()
    return text.str.contains("remote|boston|cambridge|massachusetts|, ma| ma,| ma ", regex=True)


def filter_contains(df: pd.DataFrame, column: str, query: str) -> pd.DataFrame:
    if not query:
        return df
    return df[df[column].fillna("").str.contains(query, case=False, regex=False)]


def skill_gap_summary(df: pd.DataFrame) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for value in df.get("missing_skills", pd.Series(dtype=str)).fillna(""):
        for skill in [part.strip() for part in value.split(",") if part.strip()]:
            counter[skill] += 1
    return pd.DataFrame(counter.most_common(12), columns=["missing_skill", "top_20_count"])


st.title("Data Science Job Search System")
st.caption("Public ATS collection, normalization, resume matching, Top 20 ranking, and official apply links.")

with st.spinner("Refreshing public company job boards..."):
    jobs, errors = load_jobs()

source_count = len(load_registry())
if jobs.empty:
    st.error("No jobs were returned right now. Try refreshing in a few minutes.")
    if errors:
        with st.expander("Fetch errors"):
            st.write(errors)
    st.stop()

with st.sidebar:
    st.header("Resume Match")
    uploaded_resume = st.file_uploader("Upload resume", type=["pdf", "docx", "txt", "md"])
    uploaded_text = read_uploaded_resume(uploaded_resume)
    resume_text = st.text_area(
        "Or paste resume text",
        value=uploaded_text,
        height=180,
        placeholder="Paste your resume here to calculate match scores.",
    )
    prefer_boston_remote = st.checkbox("Boston / Remote focus", value=True)
    needs_sponsorship = st.checkbox("Need visa sponsorship", value=False)

    st.header("Filters")
    title_query = st.text_input("Title contains")
    location_query = st.text_input("Location contains")
    salary_query = st.text_input("Salary contains")
    min_score = st.slider("Minimum match score", 0, 100, 0 if not resume_text.strip() else 45)
    hide_senior = st.checkbox("Hide senior / manager roles", value=True)
    salary_only = st.checkbox("Only jobs with salary text", value=False)
    families = st.multiselect("Role category", safe_options(jobs, "job_family"))
    modes = st.multiselect("Work mode", safe_options(jobs, "work_mode"))
    experiences = st.multiselect("Experience level", safe_options(jobs, "experience"))
    companies = st.multiselect("Company", safe_options(jobs, "company"))

profile = parse_resume(resume_text)
ranked_jobs = rank_jobs(
    jobs.to_dict("records"),
    profile,
    prefer_boston_remote=prefer_boston_remote,
    needs_sponsorship=needs_sponsorship,
)
ranked = pd.DataFrame(ranked_jobs)

filtered = ranked.copy()
if prefer_boston_remote:
    filtered = filtered[boston_remote_mask(filtered)]
if hide_senior:
    filtered = filtered[filtered["experience"] != "Senior / Manager"]
filtered = filter_contains(filtered, "title", title_query)
filtered = filter_contains(filtered, "location", location_query)
filtered = filter_contains(filtered, "salary", salary_query)
if salary_only:
    filtered = filtered[filtered["salary"].fillna("").str.len() > 0]
if families:
    filtered = filtered[filtered["job_family"].isin(families)]
if modes:
    filtered = filtered[filtered["work_mode"].isin(modes)]
if experiences:
    filtered = filtered[filtered["experience"].isin(experiences)]
if companies:
    filtered = filtered[filtered["company"].isin(companies)]
filtered = filtered[filtered["match_score"] >= min_score]
filtered = filtered.sort_values("match_score", ascending=False)

metric_cols = st.columns(6)
metric_cols[0].metric("live roles", f"{len(jobs):,}")
metric_cols[1].metric("filtered roles", f"{len(filtered):,}")
metric_cols[2].metric("companies", f"{jobs['company'].nunique():,}")
metric_cols[3].metric("remote roles", f"{(jobs['work_mode'] == 'Remote').sum():,}")
metric_cols[4].metric("sources", f"{source_count:,}")
metric_cols[5].metric("resume skills", f"{len(profile.skills):,}")

if not resume_text.strip():
    st.info("Upload or paste your resume to make the match score personal. Without a resume, ranking uses role, location, and experience signals only.")

display_columns = [
    "company",
    "title",
    "location",
    "salary",
    "posted_date",
    "match_score",
    "matched_skills",
    "missing_skills",
    "visa",
    "experience",
    "apply_url",
]
column_labels = {
    "company": "Company",
    "title": "Title",
    "location": "Location",
    "salary": "Salary",
    "posted_date": "Posted Date",
    "match_score": "Match Score",
    "matched_skills": "Matched Skills",
    "missing_skills": "Missing Skills",
    "visa": "Visa",
    "experience": "Experience",
    "apply_url": "Apply Link",
}

top20 = filtered.head(20)
tab_top, tab_all, tab_gaps = st.tabs(["Daily Top 20", "All Matches", "Resume Gaps"])

with tab_top:
    st.subheader("Daily Top 20")
    st.dataframe(
        top20[display_columns].rename(columns=column_labels),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Match Score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100),
            "Apply Link": st.column_config.LinkColumn("Apply Link", display_text="Apply"),
        },
    )

with tab_all:
    st.subheader(f"{len(filtered):,} matched jobs")
    st.dataframe(
        filtered[display_columns].rename(columns=column_labels),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Match Score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100),
            "Apply Link": st.column_config.LinkColumn("Apply Link", display_text="Apply"),
        },
    )
    st.download_button(
        "Download filtered CSV",
        data=filtered[display_columns].rename(columns=column_labels).to_csv(index=False).encode("utf-8"),
        file_name="data_science_jobs_ranked.csv",
        mime="text/csv",
    )

with tab_gaps:
    st.subheader("Skills most often missing from your Top 20")
    gaps = skill_gap_summary(top20)
    if gaps.empty:
        st.write("No missing skills detected for the current Top 20.")
    else:
        st.dataframe(gaps, use_container_width=True, hide_index=True)

if errors:
    with st.expander(f"{len(errors)} source or validation warnings"):
        st.write(errors[:100])

