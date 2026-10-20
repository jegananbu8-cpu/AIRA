"""Skill extraction from cleaned resume text using a controlled skill dictionary.

Uses the same alias-aware matching as job_matcher.py, so the skills shown in the
dashboard always agree with the match score and skill-gap list.
Fixes: 'C' no longer matches inside 'C++'/'C#', variants such as 'Python3',
'scikit learn', 'Open CV', 'REST API' are detected, and paths work from any folder.
"""
from pathlib import Path

import pandas as pd

from job_matcher import _normalize, skill_in_text

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SKILLS_PATH = BASE_DIR / "data" / "skill_dictionary.csv"


def load_skill_dictionary(path=DEFAULT_SKILLS_PATH):
    df = pd.read_csv(path)
    df["skill"] = df["skill"].astype(str).str.strip()
    return df.drop_duplicates("skill").reset_index(drop=True)


def extract_skills(text, skill_df):
    text_norm = _normalize(text)
    found = [{"skill": row["skill"], "category": row["category"]}
             for _, row in skill_df.iterrows()
             if skill_in_text(row["skill"], text_norm)]
    if not found:
        return pd.DataFrame(columns=["skill", "category"])
    return pd.DataFrame(found).drop_duplicates("skill").reset_index(drop=True)


def skills_by_category(skill_df):
    return skill_df.groupby("category")["skill"].apply(list).to_dict()
