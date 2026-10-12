# Deployment

This app is ready for Streamlit Community Cloud.

1. Push the repository to GitHub.
2. In Streamlit Cloud, choose `BaijieLi/data_science_jobs`.
3. Set the main file path to `app/streamlit_app.py`.
4. No secrets are required for the current public ATS sources.

The live app refreshes company job boards with a one-hour cache. If one employer temporarily blocks or rate-limits a request, the app keeps the remaining sources available and reports the skipped source in an expandable note.

