# Project Plan

## Goal

Build a practical job-search tool for data science graduates that surfaces real company-posted roles with direct application links.

## Current Features

- Fetches live roles from public company ATS APIs.
- Keeps direct company application links.
- Classifies roles into Data Scientist, Data Analyst, Machine Learning / AI, Data Engineering, and Business Intelligence.
- Separates Remote, Hybrid, On-site, and unspecified jobs.
- Labels Internship, New Grad, Entry / Associate, Professional / Unspecified, and Senior / Manager roles.
- Provides Streamlit filters and CSV export.

## Next Improvements

- Add more employers with public ATS boards.
- Add salary normalization when compensation data is present.
- Add saved-search presets for new grad, remote-only, and ML-focused searches.
- Add a scheduled GitHub Action that refreshes a static CSV snapshot.

