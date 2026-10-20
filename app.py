import streamlit as st
import pandas as pd
import plotly.express as px

from resume_parser import extract_resume_text
from text_cleaner import clean_text
from skill_extractor import load_skill_dictionary, extract_skills
from job_matcher import load_roles, calculate_role_scores, get_skill_gap, weak_skills
from roadmap_generator import generate_roadmap
from report_generator import build_report

MAX_FILE_MB = 5

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer & Job Recommendation System")
st.caption("Educational guidance tool — match scores are estimates, not hiring decisions.")
st.info(
    "Emopowering careers through intelligent resume analysis and personalized learning roadmaps."
    "Let AI understand your strengths. A missing keyword does not always mean missing ability."
)


@st.cache_data
def get_data():
    return load_skill_dictionary(), load_roles()


skill_df, roles_df = get_data()

uploaded = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
target_role = st.selectbox("Select target role", roles_df["role"].tolist())

if uploaded:
    if uploaded.size > MAX_FILE_MB * 1024 * 1024:
        st.error(f"File is larger than {MAX_FILE_MB} MB.")
        st.stop()

    try:
        raw_text = extract_resume_text(uploaded)
        text = clean_text(raw_text)

        if not text:
            st.error("No readable text was found. Scanned/image-only resumes are not supported.")
            st.stop()

        skills = extract_skills(text, skill_df)
        results = calculate_role_scores(text, roles_df, skills["skill"].tolist())
        selected = results[results["role"] == target_role].iloc[0]
        found, missing = get_skill_gap(skills["skill"].tolist(), selected)
        weak = weak_skills(text, found)
        roadmap = generate_roadmap(missing)
        total_required = len(found) + len(missing)

        st.success(f"Analyzed: {uploaded.name}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Target Match", f"{selected['match_score']:.0f}%")
        c2.metric("Required Skills Found", f"{len(found)} / {total_required}")
        c3.metric("Missing Skills", len(missing))
        c4.metric("Text Similarity", f"{selected['text_similarity']:.0f}%")

        with st.expander("How is the match score calculated?"):
            st.write(
                f"Match score = required skills found ÷ required skills for the role. "
                f"For **{target_role}**: {len(found)} of {total_required} = "
                f"{selected['match_score']:.0f}%. Text similarity (TF-IDF + cosine similarity) "
                "is shown for reference and is used only to break ties between roles."
            )

        st.subheader("🎯 Recommended Roles")
        top = results.head(3)[["role", "match_score"]]
        if top["match_score"].iloc[0] < 50:
            st.warning("No role is a strong match yet (best match is below 50%). "
                       "The roles below are the closest ones — use the roadmap to build the missing skills.")
        fig = px.bar(top, x="match_score", y="role", orientation="h",
                     range_x=[0, 100], labels={"match_score": "Match %", "role": "Role"})
        fig.update_yaxes(autorange="reversed")      # best role at the top
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(top, use_container_width=True, hide_index=True)

        left, right = st.columns(2)

        with left:
            st.subheader("✅ Skills Found in Resume")
            if skills.empty:
                st.info("No skills from the current dictionary were detected.")
            else:
                for category, group in skills.groupby("category"):
                    st.markdown(f"**{category.title()}**")
                    st.write(", ".join(group["skill"].tolist()))

        with right:
            st.subheader("⚠️ Missing Skills")
            if missing:
                for skill in missing:
                    st.write(f"- {skill}")
            else:
                st.success("No missing skills from the selected role dictionary.")
            if weak:
                st.subheader("🔎 Weak Skills")
                st.caption("Mentioned only once. Show them in a project or experience to strengthen them.")
                for skill in weak:
                    st.write(f"- {skill}")

        st.subheader("🗺️ Learning Roadmap")
        for item in roadmap:
            st.write(item)

        with st.expander("View extracted resume text"):
            st.text_area("Text", raw_text, height=250)

        report = build_report(
            target_role, selected["match_score"], skills["skill"].tolist(), missing,
            [(r["role"], r["match_score"]) for _, r in results.head(3).iterrows()], roadmap,
        )
        with st.expander("📄 Analysis Report", expanded=True):
            st.text(report)
        st.download_button("⬇️ Download Analysis Report", report,
                           file_name="resume_analysis.txt", mime="text/plain")

    except Exception as e:
        st.error(f"Could not analyze the resume: {e}")

else:
    st.info("Upload a PDF or DOCX resume to begin.")
    st.subheader("How it works")
    st.write("Upload → Extract → Clean → Detect Skills → Match Roles → Find Gaps → Generate Roadmap")
