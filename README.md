# AI Resume Analyzer & Job Recommendation System

An educational NLP application. A student uploads a **PDF or DOCX resume**, picks a target job role, and gets:
a **match score**, **skills found**, **missing and weak skills**, the **top three recommended roles**, a
**week-by-week learning roadmap**, and a **downloadable report**.

> Guidance tool only. Match scores are estimates, **not** hiring or rejection decisions, and a missing keyword
> does not always mean missing ability.

![Architecture](docs/architecture.png)

## Features
- PDF and DOCX upload (type and 5 MB size validation); text is read from every PDF page, DOCX paragraph and DOCX table
- Text cleaning that keeps technical symbols such as `C++`, `C#`, `.NET`
- Skill extraction from a 57-skill dictionary in 10 categories, with aliases (`Python3`, `scikit learn`, `Open CV`, `REST API`, ...)
- Comparison with 5 job roles; top-3 role recommendation
- Skill-gap analysis: found, missing and weak skills (mentioned only once)
- Rule-based learning roadmap, ordered from basic to advanced
- Streamlit dashboard with match chart and a "How is the score calculated?" explanation
- Downloadable analysis report (.txt)

## Example output
The downloaded report (resume `Resume_A_Data_Analyst`, target role *Machine Learning Engineer*):
```
Target Role: Machine Learning Engineer
Resume Match Score: 20%

Skills Found:
- Python
- SQL
- MySQL
- Excel
- Pandas
- NumPy
- Power BI
- Tableau
- Git

Missing Skills:
- Machine Learning
- scikit-learn
- FastAPI
- Docker

Recommended Roles:
1. Data Analyst - 100%
2. Computer Vision Engineer - 25%
3. NLP Engineer - 25%

Suggested Roadmap:
Week 1: Machine learning fundamentals
Week 2: Model building with scikit-learn
Week 3: FastAPI basics
Week 4: Deploy an ML model and Docker fundamentals
```

## How the match score works
```
Match score = required skills found in the resume / required skills for the role x 100
```
Example: a Data Analyst needs Python, SQL, Excel, Pandas, Power BI. A resume with 4 of them scores 80%.

**TF-IDF + cosine similarity** between the resume and the role description is also calculated. It is shown as
*Text Similarity* and used only to break ties between roles. It is not the main score because it falls as a resume
gets longer, even when every required skill is present.

## Run locally
```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```
Try the files in `sample_resumes/` first.

## Run the tests
```bash
python tests/run_tests.py
```
This checks every sample resume (PDF and DOCX), skill precision and recall, fairness, score consistency and
edge cases, and writes `tests/evaluation_sheet.csv`.

## Project structure
```
ai_resume_analyzer/
|-- app.py                  Streamlit dashboard
|-- resume_parser.py        PDF / DOCX text extraction
|-- text_cleaner.py         text cleaning
|-- skill_extractor.py      dictionary + alias skill detection
|-- job_matcher.py          skill-coverage score, TF-IDF similarity, skill gap, weak skills
|-- roadmap_generator.py    rule-based learning roadmap (one topic per week)
|-- report_generator.py     builds the text report in the guide's output format
|-- data/                   job_roles.csv, skill_dictionary.csv
|-- sample_resumes/         6 fictional resumes (PDF + DOCX), personal details removed
|-- tests/                  run_tests.py, evaluation_sheet.csv, sample_resume_truth.csv, test_cases.csv
|-- docs/                   architecture.png, PROJECT_REPORT.md, VIVA_ANSWERS.md
|-- reports/                sample_report_ResumeA_for_ML_Engineer.txt (example of the downloaded report)
`-- requirements.txt, README.md, .env, .gitignore
```

## Customise
- **Add a role:** add a row to `data/job_roles.csv` (`role, description, required_skills`).
- **Add a skill:** add a row to `data/skill_dictionary.csv`; add spelling variants to `SKILL_ALIASES` in `job_matcher.py`;
  add a learning topic to `ROADMAP` in `roadmap_generator.py`.

## Deploy (Streamlit Community Cloud)
1. Push this folder to a public GitHub repository.
2. On https://share.streamlit.io choose **New app**, select the repository and set the main file to `app.py`.

## Responsible AI
- Used for guidance, never for automatic hiring or rejection.
- Gender, age, religion, nationality, photograph, marital status and disability are not scored; such terms are also
  removed before the text-similarity step. A test checks that adding them does not change any score.
- Only job-related skills, education, projects and experience matter.
- Resumes are processed in memory and are not stored.

## Limitations
- Only skills in the dictionary are detected; synonyms not listed as aliases are missed.
- Skills are matched by keywords, so the tool cannot judge how well someone knows a skill.
- Scanned (image-only) PDFs have no text to read and are not supported.
- Only 5 roles are included, with short manually written skill lists.
- Tested on 6 fictional sample resumes, which is a small set.

## Future work
Sentence Transformers for semantic matching, spaCy entity extraction, resume section detection,
job-description upload, a PDF report, an LLM-based feedback layer, and a FastAPI backend with Docker.
