from __future__ import annotations

import csv
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from data_science_jobs.pipeline import build_job_board  # noqa: E402


OUTPUT_DIR = REPO_ROOT / "outputs"
CSV_PATH = OUTPUT_DIR / "data_science_jobs.csv"
JSON_PATH = OUTPUT_DIR / "data_science_jobs.json"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rows, errors = build_job_board()
    OUTPUT_DIR.mkdir(exist_ok=True)
    fieldnames = [
        "company",
        "title",
        "location",
        "salary",
        "work_mode",
        "experience",
        "visa",
        "job_family",
        "domain",
        "department",
        "employment_type",
        "apply_url",
        "source",
        "posted_date",
        "application_url",
        "posting_url",
        "provider",
        "published_at",
        "updated_at",
    ]
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    with JSON_PATH.open("w") as f:
        json.dump(rows, f, indent=2)

    print(f"Wrote {len(rows)} data-science jobs to {CSV_PATH}")
    print(f"Companies with temporary fetch errors: {len(errors)}")
    for error in errors[:10]:
        print(f"- {error}")


if __name__ == "__main__":
    main()
