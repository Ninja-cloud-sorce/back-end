from __future__ import annotations

from typing import Dict, List, Set
import re

# Simple, extensible skills list (can be replaced/enhanced by AI models)
KNOWN_SKILLS: Set[str] = {
    "python", "fastapi", "flask", "django", "sql", "nosql", "mongodb", "postgresql",
    "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "github actions",
    "unit testing", "pytest", "rest", "graphql", "redis", "celery", "rabbitmq",
    "nlp", "machine learning", "data science", "pandas", "numpy", "transformers",
}


_WORD_SPLIT_RE = re.compile(r"[^a-zA-Z0-9\+\#]+")


def _normalize(text: str) -> List[str]:
    tokens = [t.strip().lower() for t in _WORD_SPLIT_RE.split(text) if t.strip()]
    # merge common two-word skills if present separated in text (very naive)
    merged: List[str] = []
    i = 0
    while i < len(tokens):
        current = tokens[i]
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if nxt and f"{current} {nxt}" in KNOWN_SKILLS:
            merged.append(f"{current} {nxt}")
            i += 2
        else:
            merged.append(current)
            i += 1
    return merged


def _extract_skills(text: str) -> Set[str]:
    tokens = _normalize(text)
    present = set()
    for token in tokens:
        if token in KNOWN_SKILLS:
            present.add(token)
    return present


def analyze_resume(resume_text: str, job_description: str) -> Dict[str, object]:
    """
    Dummy analyzer with clean interface. Replace internals with OpenAI/HF later.

    Returns keys: match_percent, missing_skills, suggestions, ats_score
    """
    resume_skills = _extract_skills(resume_text)
    job_skills = _extract_skills(job_description)

    if not job_skills:
        # Fallback: estimate match based on token overlap
        resume_tokens = set(_normalize(resume_text))
        job_tokens = set(_normalize(job_description))
        overlap = len(resume_tokens & job_tokens)
        denom = max(1, len(job_tokens))
        match_percent = round(100.0 * overlap / denom, 1)
        missing_skills: List[str] = []
    else:
        overlap = len(resume_skills & job_skills)
        denom = max(1, len(job_skills))
        match_percent = round(100.0 * overlap / denom, 1)
        missing_skills = sorted(list(job_skills - resume_skills))

    suggestions: List[str] = []
    if match_percent < 60:
        suggestions.append(
            "Highlight relevant experience and quantify achievements with metrics (%, $, time)."
        )
    if missing_skills:
        suggestions.append(
            f"Consider learning or emphasizing: {', '.join(missing_skills[:8])}"
        )
    if "python" in resume_skills and "fastapi" not in resume_skills:
        suggestions.append("Add FastAPI projects or APIs to showcase backend skills.")
    if "docker" in resume_skills and "kubernetes" not in resume_skills:
        suggestions.append("Explore Kubernetes basics to complement Docker skills.")

    # Simple ATS score: start from match_percent and subtract small penalties per missing skill
    penalty = min(30.0, 5.0 * len(missing_skills))
    ats_score = round(max(0.0, min(100.0, match_percent - penalty)), 1)

    return {
        "match_percent": match_percent,
        "missing_skills": missing_skills,
        "suggestions": suggestions or [
            "Great alignment. Ensure resume is concise (1-2 pages) and well-formatted."
        ],
        "ats_score": ats_score,
    }


def suggest_growth_path(resume_text: str) -> Dict[str, List[str]]:
    skills = _extract_skills(resume_text)
    path: List[str] = []

    if "fastapi" in skills or "flask" in skills:
        path.append("Deepen API design: auth, rate limiting, versioning, observability.")
        path.append("Add async patterns, background jobs (Celery/RQ), and caching (Redis).")
    if "python" in skills:
        path.append("Master typing (PEP 484), testing (pytest), and packaging.")
    if "aws" in skills or "gcp" in skills or "azure" in skills:
        path.append("Build CI/CD pipelines and infrastructure as code (Terraform).")
    if "nlp" in skills or "machine learning" in skills:
        path.append("Productionize ML: model serving, monitoring, and data pipelines.")

    if not path:
        path = [
            "Identify target role, collect 5 job descriptions, and extract required skills.",
            "Close top 3 skill gaps via focused projects and certifications.",
            "Publish projects with READMEs, tests, and live demos (Render/Heroku/Fly).",
        ]

    return {"growth_path": path}


def optimize_resume(resume_text: str) -> str:
    lines = [l.strip() for l in (resume_text or "").splitlines() if l.strip()]
    bulletized = [l if l.startswith("-") else f"- {l}" for l in lines]
    header = "SUMMARY\nResults-driven professional with measurable achievements.\n"
    return header + "\n".join(bulletized)


def generate_cover_letter_text(resume_text: str, job_desc: str) -> str:
    overlap = sorted(list(_extract_skills(resume_text) & _extract_skills(job_desc)))
    highlights = ", ".join(overlap) if overlap else "relevant experience"
    return (
        "Dear Hiring Manager,\n\n"
        "I am excited to apply for this role. My background aligns with your needs, including "
        f"{highlights}. I deliver impact through ownership, collaboration, and measurable outcomes.\n\n"
        "Sincerely,\nYour Name"
    )
