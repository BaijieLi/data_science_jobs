from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
DIRECTORY_URL = "https://kalebconfer-sys.github.io/job-board-directory/job-board-directory.json"


def load_existing_keys() -> set[tuple[str, str]]:
    with (REPO_ROOT / "data" / "source_registry.json").open() as f:
        rows = json.load(f)
    return {(row["provider"], row["board"]) for row in rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Find candidate ATS boards from a public job-board directory.")
    parser.add_argument("keywords", nargs="+", help="Company, region, or industry keywords to search for.")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    response = requests.get(DIRECTORY_URL, timeout=30)
    response.raise_for_status()
    directory = response.json()
    existing = load_existing_keys()
    keywords = [keyword.lower() for keyword in args.keywords]

    matches = []
    for row in directory:
        haystack = " ".join(str(row.get(field, "")) for field in ("company", "token", "board_url")).lower()
        if not any(keyword in haystack for keyword in keywords):
            continue
        key = (row["platform"], row["token"].split("/")[-1])
        status = "existing" if key in existing else "candidate"
        matches.append(
            {
                "status": status,
                "company": row["company"],
                "provider": row["platform"],
                "token": row["token"],
                "open_roles": row.get("open_roles"),
                "api_url": row.get("api_url"),
                "board_url": row.get("board_url"),
            }
        )

    json.dump(matches[: args.limit], sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()

