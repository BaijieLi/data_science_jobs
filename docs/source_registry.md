# Source Registry

The app uses company-operated applicant tracking systems rather than scraped search-result pages. Each row in `data/source_registry.json` contains:

- `company`: display name
- `provider`: `greenhouse`, `ashby`, `lever`, `workday`, `workable`, `recruitee`, `personio`, `rippling`, or `smartrecruiters`
- `board`: public board identifier used by the ATS endpoint
- `focus`: a short description used for domain classification

The first release includes AI, data infrastructure, fintech, consumer marketplace, healthcare, civic-tech, gaming, travel, payments, and consulting employers. The registry can be extended by adding another company object if its public ATS board is available.

## Expansion Strategy

The project favors sources that meet three conditions:

- The job source is operated by the employer or its ATS provider.
- The posting includes a stable application URL.
- The endpoint can be fetched without a private API key or login.

Large global job boards such as LinkedIn, Indeed, and Google Jobs are useful for discovery, but they are not the preferred automated source here because postings often redirect, deduplicate, or obscure the original company application URL.

Use `python scripts/discover_candidate_sources.py <keyword>` to search a public ATS directory for candidate company boards before adding another source.
