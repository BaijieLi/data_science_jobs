from __future__ import annotations

import re


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "SQL": ("sql", "postgres", "postgresql", "mysql", "sqlite", "snowflake sql", "bigquery"),
    "R": (" r ", "r programming", "tidyverse"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "Scikit-learn": ("scikit-learn", "sklearn"),
    "Machine Learning": ("machine learning", "ml model", "predictive modeling"),
    "Statistics": ("statistics", "statistical", "hypothesis testing", "regression"),
    "A/B Testing": ("a/b testing", "ab testing", "experiment design", "experimentation"),
    "Tableau": ("tableau",),
    "Power BI": ("power bi", "powerbi"),
    "Looker": ("looker", "lookml"),
    "Excel": ("excel", "spreadsheet"),
    "ETL": ("etl", "elt", "data pipeline", "data pipelines"),
    "Airflow": ("airflow",),
    "dbt": ("dbt",),
    "Spark": ("spark", "pyspark"),
    "Databricks": ("databricks",),
    "AWS": ("aws", "s3", "redshift", "glue", "sagemaker"),
    "GCP": ("gcp", "google cloud", "bigquery", "vertex ai"),
    "Azure": ("azure",),
    "Docker": ("docker",),
    "Git": ("git", "github", "gitlab"),
    "Data Quality": ("data quality", "validation", "data validation", "quality checks"),
    "Data Visualization": ("data visualization", "visualization", "dashboard", "dashboards"),
    "NLP": ("nlp", "natural language processing", "llm", "language model"),
    "Deep Learning": ("deep learning", "neural network", "pytorch", "tensorflow"),
}


def _contains_alias(text: str, alias: str) -> bool:
    if alias.strip() != alias:
        return alias in f" {text} "
    return re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", text, flags=re.I) is not None


def extract_skills(text: str) -> set[str]:
    normalized = f" {re.sub(r'[^a-z0-9+#./ -]+', ' ', (text or '').lower())} "
    skills = set()
    for skill, aliases in SKILL_ALIASES.items():
        if any(_contains_alias(normalized, alias.lower()) for alias in aliases):
            skills.add(skill)
    return skills


def compare_skills(resume_skills: set[str], job_text: str) -> tuple[list[str], list[str], list[str]]:
    job_skills = extract_skills(job_text)
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    return matched, missing, sorted(job_skills)

