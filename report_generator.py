"""Build the text analysis report in the format given in the project guide."""

NOTE = ("Note: match scores are estimates for educational guidance, not recruiter decisions. "
        "A missing keyword does not always mean missing ability.")


def _bullets(items):
    return "\n".join(f"- {x}" for x in items) if items else "- None"


def build_report(target_role, match_score, skills_found, missing_skills, recommended_roles, roadmap):
    """recommended_roles: list of (role, score) already sorted best first.
    roadmap: list of 'Week N: ...' strings."""
    roles = "\n".join(f"{i}. {role} - {score:.0f}%" for i, (role, score) in enumerate(recommended_roles, 1))
    return (
        f"Target Role: {target_role}\n"
        f"Resume Match Score: {match_score:.0f}%\n\n"
        f"Skills Found:\n{_bullets(skills_found)}\n\n"
        f"Missing Skills:\n{_bullets(missing_skills)}\n\n"
        f"Recommended Roles:\n{roles}\n\n"
        f"Suggested Roadmap:\n" + "\n".join(roadmap) + "\n\n" + NOTE + "\n"
    )
