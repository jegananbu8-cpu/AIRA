"""Rule-based learning roadmap: one short topic per week, ordered from basic to advanced."""

# skill -> list of learning steps (short topics)
STEPS = {
    "python": ["Python fundamentals"],
    "sql": ["SQL queries and joins"],
    "excel": ["Excel formulas and pivot tables"],
    "pandas": ["Pandas data cleaning"],
    "numpy": ["NumPy basics"],
    "power bi": ["Power BI dashboards"],
    "tableau": ["Tableau dashboards"],
    "statistics": ["Statistics basics"],
    "machine learning": ["Machine learning fundamentals"],
    "scikit-learn": ["Model building with scikit-learn"],
    "deep learning": ["Deep learning fundamentals"],
    "nlp": ["NLP fundamentals"],
    "transformers": ["Transformers basics"],
    "hugging face": ["Hugging Face models"],
    "opencv": ["Image processing with OpenCV"],
    "cnn": ["CNN fundamentals"],
    "yolo": ["Object detection with YOLO"],
    "llm": ["LLM fundamentals"],
    "rag": ["RAG with vector search"],
    "apis": ["REST API basics"],
    "fastapi": ["FastAPI basics", "Deploy an ML model"],
    "docker": ["Docker fundamentals"],
    "mlflow": ["MLflow"],
    "git": ["Git and GitHub"],
    "kubernetes": ["Kubernetes basics"],
    "ci/cd": ["CI/CD pipelines"],
}

# Basic -> advanced. Skills not listed here go last, in their original order.
LEARNING_ORDER = [
    "python", "sql", "excel", "statistics", "numpy", "pandas", "git",
    "power bi", "tableau", "machine learning", "scikit-learn", "deep learning",
    "nlp", "opencv", "cnn", "yolo", "transformers", "hugging face", "llm", "rag",
    "apis", "fastapi", "docker", "mlflow", "ci/cd", "kubernetes",
]

_KNOWN_WORDS = {k.split()[0] for k in STEPS}


def _order_key(skill):
    s = skill.lower()
    return LEARNING_ORDER.index(s) if s in LEARNING_ORDER else len(LEARNING_ORDER)


def _soften(step):
    """Lower-case a generic first word when steps are joined ('... and cloud deployment')."""
    first = step.split()[0]
    if first.lower() in _KNOWN_WORDS or any(c.isupper() for c in first[1:]):
        return step
    return step[0].lower() + step[1:]


def _join(steps):
    parts = [steps[0]] + [_soften(s) for s in steps[1:]]
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def generate_roadmap(missing_skills, weeks=4):
    if not missing_skills:
        return ["No major skill gaps detected. Build projects to strengthen your existing skills."]
    steps = []
    for skill in sorted(missing_skills, key=_order_key):          # stable sort
        steps.extend(STEPS.get(skill.lower(), [skill]))
    used = min(len(steps), weeks)
    base, extra = divmod(len(steps), used)
    roadmap, start = [], 0
    for week in range(1, used + 1):
        size = base + (1 if week > used - extra else 0)           # extra steps go in the last weeks
        roadmap.append(f"Week {week}: {_join(steps[start:start + size])}")
        start += size
    return roadmap
