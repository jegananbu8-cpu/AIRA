"""Job matching: skill-coverage score + TF-IDF text similarity.

Match score (0-100) = percentage of the role's required skills found in the resume.
It is explainable ("4 of 5 required skills found = 80%") and does NOT drop when a
resume is long. TF-IDF cosine similarity is kept as a secondary, informational value
and as a tie-breaker when two roles have the same coverage.

Protected personal attributes (gender, age, religion, marital status, ...) are
removed before any text comparison and are never used as skills.
"""
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ROLES_PATH = BASE_DIR / "data" / "job_roles.csv"

# Different ways a resume may write the same skill (all lowercase).
SKILL_ALIASES = {
    "python": ["python3", "python 3"],
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["deep-learning"],
    "scikit-learn": ["scikit learn", "sklearn", "scikitlearn"],
    "opencv": ["open cv", "cv2"],
    "hugging face": ["huggingface", "hugging-face"],
    "power bi": ["powerbi", "power-bi"],
    "apis": ["api", "rest api", "rest apis", "restful api", "restful apis"],
    "nlp": ["natural language processing"],
    "llm": ["llms", "large language model", "large language models"],
    "rag": ["retrieval augmented generation", "retrieval-augmented generation"],
    "cnn": ["cnns", "convolutional neural network", "convolutional neural networks"],
    "postgresql": ["postgres"],
    "javascript": ["js"],
    "transformers": ["transformer"],
    "fastapi": ["fast api"],
    "github": ["git hub"],
}

# Words that must never influence a score (Responsible AI rule).
_PROTECTED = re.compile(
    r"\b(male|female|gender|sex|age|aged|years old|yrs old|dob|date of birth|"
    r"religion|hindu|muslim|christian|sikh|buddhist|jain|nationality|indian|"
    r"marital status|married|unmarried|single|divorced|disability|disabled|"
    r"photograph|photo|caste|father'?s? name|mother'?s? name)\b"
)


def load_roles(path=DEFAULT_ROLES_PATH):
    return pd.read_csv(path)


def _normalize(text):
    """Lowercase and make hyphens/underscores/slashes comparable, keep c++ c# .net."""
    text = str(text).lower()
    text = re.sub(r"[-_/]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def remove_protected_terms(text):
    return re.sub(_PROTECTED, " ", _normalize(text))


def _pattern(term):
    # (?![a-z0-9+#]) stops 'c' matching inside 'c++' / 'c#' and 'java' inside 'javascript'.
    return rf"(?<![a-z0-9+#.]){re.escape(_normalize(term))}(?![a-z0-9+#])"


def skill_in_text(skill, text_norm):
    names = [skill] + SKILL_ALIASES.get(_normalize(skill), [])
    return any(re.search(_pattern(n), text_norm) for n in names)


def skill_mention_count(skill, text_norm):
    """How many separate times a skill (or an alias) is mentioned."""
    names = [skill] + SKILL_ALIASES.get(_normalize(skill), [])
    ends = set()
    for n in names:
        ends.update(m.end() for m in re.finditer(_pattern(n), text_norm))
    return len(ends)


def weak_skills(resume_text, matched_skills):
    """Matched skills that appear only once (e.g. only in a skills list, never in a project)."""
    text_norm = _normalize(resume_text)
    return [s for s in matched_skills if skill_mention_count(s, text_norm) == 1]


def required_skills(row):
    return [s.strip() for s in str(row["required_skills"]).split(",") if s.strip()]


def calculate_role_scores(resume_text, roles_df, extracted_skills=None):
    """Return roles ranked by match_score, with matched/missing skills per role."""
    text_norm = _normalize(resume_text)
    extracted = {_normalize(s) for s in (extracted_skills or [])}

    # Text similarity uses only job-related text with protected terms removed.
    safe_text = remove_protected_terms(resume_text)
    corpus = [safe_text] + [f"{r['role']} {r['description']} {r['required_skills']}"
                            for _, r in roles_df.iterrows()]
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(corpus)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except ValueError:                      # empty vocabulary
        sims = [0.0] * len(roles_df)

    rows = []
    for (_, role), sim in zip(roles_df.iterrows(), sims):
        req = required_skills(role)
        matched = [s for s in req if _normalize(s) in extracted or skill_in_text(s, text_norm)]
        missing = [s for s in req if s not in matched]
        coverage = 100 * len(matched) / len(req) if req else 0.0
        rows.append({**role.to_dict(),
                     "match_score": round(coverage, 1),
                     "text_similarity": round(float(sim) * 100, 1),
                     "matched_skills": matched,
                     "missing_skills": missing})
    result = pd.DataFrame(rows)
    return (result.sort_values(["match_score", "text_similarity"], ascending=False)
                  .reset_index(drop=True))


def get_skill_gap(extracted_skills, selected_role_row):
    """Return (found, missing). Uses the score's own result when available so the
    score and the gap list can never disagree."""
    if "matched_skills" in selected_role_row and "missing_skills" in selected_role_row:
        found = list(selected_role_row["matched_skills"])
        missing = list(selected_role_row["missing_skills"])
        # also accept skills the extractor found that the text match missed
        have = {_normalize(s) for s in extracted_skills}
        moved = [s for s in missing if _normalize(s) in have]
        return found + moved, [s for s in missing if s not in moved]
    have = {_normalize(s) for s in extracted_skills}
    req = required_skills(selected_role_row)
    return ([s for s in req if _normalize(s) in have],
            [s for s in req if _normalize(s) not in have])
