# Global Job Boards and Search Links

These sources are useful for manual search expansion. The app prioritizes company ATS links, but these boards help discover new companies to add to `data/source_registry.json`.

## Broad Global Boards

- LinkedIn Jobs: https://www.linkedin.com/jobs/search/?keywords=data%20scientist
- Indeed: https://www.indeed.com/jobs?q=data+scientist
- Google Jobs: search Google for `data scientist jobs remote` or `machine learning engineer new grad`.
- Glassdoor: https://www.glassdoor.com/Job/data-scientist-jobs-SRCH_KO0,14.htm
- Wellfound: https://wellfound.com/jobs
- Otta / Welcome to the Jungle: https://app.otta.com/jobs
- Levels.fyi Jobs: https://www.levels.fyi/jobs/

## Data / AI Specific

- AI Jobs: https://ai-jobs.net/
- Data Science Jobs: https://www.datasciencejobs.com/
- Data Elixir Jobs: https://dataelixir.com/jobs
- Kaggle Jobs discussions/search: https://www.kaggle.com/discussions
- Machine Learning Jobs subreddit: https://www.reddit.com/r/MachineLearningJobs/

## Remote and Worldwide

- Remote OK: https://remoteok.com/remote-data-jobs
- We Work Remotely: https://weworkremotely.com/categories/remote-programming-jobs
- Remotive: https://remotive.com/remote-jobs/software-dev
- Remote.co: https://remote.co/remote-jobs/developer/
- Working Nomads: https://www.workingnomads.com/jobs

## Regional Boards

- Built In: https://builtin.com/jobs
- EU-Startups Jobs: https://www.eu-startups.com/job/
- Japan Dev: https://japan-dev.com/jobs
- Tech in Asia Jobs: https://www.techinasia.com/jobs
- SEEK Australia / New Zealand: https://www.seek.com.au/data-scientist-jobs
- Otta UK/EU/US startup search: https://app.otta.com/jobs
- AngelList / Wellfound startup search: https://wellfound.com/jobs

## How To Add A New Company Source

1. Find the company's careers page.
2. Identify the ATS provider from the URL, such as Greenhouse, Ashby, Lever, Workday, Workable, Personio, Recruitee, Rippling, or SmartRecruiters.
3. Add the company object to `data/source_registry.json`.
4. Run `python scripts/fetch_live_jobs.py`.
5. Keep the source only if it returns original application links and relevant data/AI/analytics roles.

