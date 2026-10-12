# Job Search System

## Flow

```text
Public ATS and company career pages
        |
        v
Collectors: Greenhouse, Lever, Ashby, Workday, Workable, SmartRecruiters
        |
        v
Normalize, validate, deduplicate
        |
        v
Filter: Boston / Remote, role family, salary, company, experience
        |
        v
Resume parser extracts skills and location hints
        |
        v
Ranking: skill overlap, missing skills, role relevance, location, visa, experience
        |
        v
Daily Top 20 with official company apply links
```

## Common Job Schema

- `title`
- `company`
- `location`
- `salary`
- `description`
- `posted_date`
- `source`
- `apply_url`

The dashboard also adds:

- `match_score`
- `matched_skills`
- `missing_skills`
- `visa`
- `experience`
- `job_family`
- `work_mode`

## Matching Logic

The MVP uses transparent heuristic scoring:

- Skill match: resume skills that appear in the job title or description.
- Missing skills: job skills not found in the resume.
- Role relevance: Data Analyst, Data Quality, Junior Data Engineering, Data Scientist, ML, and BI roles are weighted differently.
- Location: Boston, Cambridge, Massachusetts, and Remote are prioritized by default.
- Experience: New Grad, Entry, Associate, Internship, and unspecified roles are favored over senior/manager roles.
- Visa: sponsorship language is detected when present.

This is intentionally not an auto-apply tool. It helps identify and prioritize jobs, then the user clicks the official company application link and submits manually.

## Excluded Sources

The project does not scrape LinkedIn or Handshake. It prefers public APIs/endpoints and employer-operated ATS pages.

