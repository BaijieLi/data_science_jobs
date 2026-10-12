# Source Registry

The app uses company-operated applicant tracking systems rather than scraped search-result pages. Each row in `data/source_registry.json` contains:

- `company`: display name
- `provider`: `greenhouse`, `ashby`, or `lever`
- `board`: public board identifier used by the ATS endpoint
- `focus`: a short description used for domain classification

The first release includes AI, data infrastructure, fintech, consumer marketplace, healthcare, and civic-tech employers. The registry can be extended by adding another company object if its public ATS board is available.

