# Project Plan

## Goal

Build a practical job-search system for data science graduates that surfaces real company-posted roles with direct application links, resume matching, and daily ranked recommendations.

## Current Features

- Fetches live roles from public company ATS APIs across Greenhouse, Ashby, Lever, Workday, Workable, Rippling, Personio, Recruitee, and SmartRecruiters.
- Keeps direct company application links.
- Normalizes jobs into a common schema.
- Deduplicates and validates jobs.
- Classifies roles into Data Scientist, Data Analyst, Machine Learning / AI, Data Engineering, and Business Intelligence.
- Separates Remote, Hybrid, On-site, and unspecified jobs.
- Labels Internship, New Grad, Entry / Associate, Professional / Unspecified, and Senior / Manager roles.
- Parses resume text or uploaded PDF/DOCX/TXT/MD resumes.
- Scores jobs by skills, missing skills, role relevance, Boston/Remote preference, experience level, and visa signal.
- Provides Streamlit filters, Daily Top 20, resume skill-gap summary, and CSV export.

## Next Improvements

- Continue expanding employers with public ATS boards, especially APAC, LATAM, EU, and public-sector data organizations.
- Add salary normalization when compensation data is present.
- Add saved-search presets for new grad, remote-only, and ML-focused searches.
- Add a scheduled GitHub Action that refreshes a static CSV snapshot.
- Add human-approved resume bullet tailoring based on top missing skills.
