"""
Utility package initialization.
"""
from .skills_database import (
    SKILLS_TAXONOMY,
    SKILL_ALIASES,
    get_all_skills,
    get_skill_categories,
    canonicalize_skill,
    get_skill_category_map
)
from .helpers import (
    clean_text,
    extract_email,
    extract_phone,
    extract_links,
    extract_sections,
    SAMPLE_RESUMES,
    SAMPLE_JOB_DESCRIPTIONS
)

__all__ = [
    "SKILLS_TAXONOMY",
    "SKILL_ALIASES",
    "get_all_skills",
    "get_skill_categories",
    "canonicalize_skill",
    "get_skill_category_map",
    "clean_text",
    "extract_email",
    "extract_phone",
    "extract_links",
    "extract_sections",
    "SAMPLE_RESUMES",
    "SAMPLE_JOB_DESCRIPTIONS"
]
