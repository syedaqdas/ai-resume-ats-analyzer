"""
Matcher module for AI Resume ATS Analyzer.
Performs semantic skill gap analysis, TF-IDF cosine similarity,
and experience requirement parsing between Resume and Job Description.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyzer.resume_parser import ResumeData
from analyzer.skill_extractor import SkillExtractor


@dataclass
class JobDescriptionData:
    """Structured representation of parsed job description."""
    raw_text: str
    cleaned_text: str
    skills: List[str] = field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = field(default_factory=dict)
    skill_frequencies: Dict[str, int] = field(default_factory=dict)
    min_experience_years: float = 0.0
    max_experience_years: float = 0.0
    required_education: List[str] = field(default_factory=list)
    top_keywords: List[str] = field(default_factory=list)


@dataclass
class MatchResult:
    """Detailed matching results comparing resume against job description."""
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_skills: List[str] = field(default_factory=list)
    category_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    keyword_similarity: float = 0.0
    top_matching_keywords: List[Tuple[str, float]] = field(default_factory=list)
    missing_critical_keywords: List[str] = field(default_factory=list)
    skill_match_percentage: float = 0.0
    experience_match_score: float = 0.0
    project_relevance_score: float = 0.0
    jd_min_exp: float = 0.0
    candidate_exp: float = 0.0


class JobDescriptionParser:
    """Parses Job Description text to identify requirements and keywords."""

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def parse(self, text: str) -> JobDescriptionData:
        """Parses job description text into structured data."""
        cleaned = text.strip()
        skills, categorized, freqs = self.skill_extractor.extract_skills(cleaned)
        min_exp, max_exp = self._extract_experience_requirement(cleaned)
        education = self._extract_education_requirements(cleaned)
        top_keywords = self._extract_top_keywords(cleaned)

        return JobDescriptionData(
            raw_text=text,
            cleaned_text=cleaned,
            skills=skills,
            categorized_skills=categorized,
            skill_frequencies=freqs,
            min_experience_years=min_exp,
            max_experience_years=max_exp,
            required_education=education,
            top_keywords=top_keywords
        )

    def _extract_experience_requirement(self, text: str) -> Tuple[float, float]:
        """
        Extracts minimum and maximum years of required experience (e.g. '3-5 years', '5+ years').
        """
        # Range pattern: 3 to 5 years, 3-5 yrs
        range_pattern = r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)"
        range_match = re.search(range_pattern, text, re.IGNORECASE)
        if range_match:
            min_yr = float(range_match.group(1))
            max_yr = float(range_match.group(2))
            return min_yr, max_yr

        # Single bound pattern: 5+ years, at least 3 years, minimum 4 years
        single_pattern = r"(?:at least|minimum|min|over)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)(?:\s+of)?\s+experience"
        single_match = re.search(single_pattern, text, re.IGNORECASE)
        if single_match:
            min_yr = float(single_match.group(1))
            return min_yr, min_yr + 2.0

        return 0.0, 0.0

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extracts degrees mentioned in the job description."""
        education = []
        degree_patterns = [
            (r"\b(?:Ph\.?D|Doctorate)\b", "PhD"),
            (r"\b(?:Master'?s|M\.?S|M\.?Sc|MBA)\b", "Master's"),
            (r"\b(?:Bachelor'?s|B\.?S|B\.?Sc|B\.?Tech|B\.?E)\b", "Bachelor's"),
        ]
        for pat, label in degree_patterns:
            if re.search(pat, text, re.IGNORECASE):
                education.append(label)
        return education

    def _extract_top_keywords(self, text: str, max_features: int = 25) -> List[str]:
        """Uses TF-IDF to identify the most salient domain keywords in the JD."""
        if not text:
            return []
        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=max_features,
                token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.-]{1,}\b"
            )
            vectorizer.fit([text])
            feature_names = vectorizer.get_feature_names_out()
            return list(feature_names)
        except Exception:
            return []


class ResumeMatcher:
    """
    Compares candidate ResumeData with JobDescriptionData to produce MatchResult.
    """

    def __init__(self):
        self.jd_parser = JobDescriptionParser()

    def match(self, resume: ResumeData, jd: JobDescriptionData) -> MatchResult:
        """
        Performs full matching evaluation across skills, keywords, experience, and projects.
        """
        resume_skills_set = set(resume.skills)
        jd_skills_set = set(jd.skills)

        # 1. Skill Gap Analysis
        matched_skills = sorted(list(resume_skills_set.intersection(jd_skills_set)))
        missing_skills = sorted(list(jd_skills_set - resume_skills_set))
        extra_skills = sorted(list(resume_skills_set - jd_skills_set))

        # Skill match percentage (40% weight driver)
        if len(jd_skills_set) > 0:
            skill_match_percentage = (len(matched_skills) / len(jd_skills_set)) * 100.0
        else:
            skill_match_percentage = 100.0 if len(resume_skills_set) > 0 else 0.0

        # Category Breakdown
        category_breakdown = {}
        for cat, jd_cat_skills in jd.categorized_skills.items():
            if not jd_cat_skills:
                continue
            matched_in_cat = [s for s in jd_cat_skills if s in resume_skills_set]
            missing_in_cat = [s for s in jd_cat_skills if s not in resume_skills_set]
            match_pct = (len(matched_in_cat) / len(jd_cat_skills)) * 100.0 if jd_cat_skills else 100.0
            category_breakdown[cat] = {
                "total_required": len(jd_cat_skills),
                "matched_count": len(matched_in_cat),
                "missing_count": len(missing_in_cat),
                "matched_skills": matched_in_cat,
                "missing_skills": missing_in_cat,
                "match_percentage": round(match_pct, 1)
            }

        # 2. Keyword Cosine Similarity (TF-IDF)
        keyword_similarity, top_matching_keywords = self._compute_keyword_similarity(
            resume.cleaned_text, jd.cleaned_text
        )

        # Identify missing critical keywords from JD
        missing_critical_keywords = [
            kw for kw in jd.top_keywords
            if kw.lower() not in resume.cleaned_text.lower()
        ][:8]

        # 3. Experience Match Score
        exp_score = self._compute_experience_score(resume.experience_years, jd.min_experience_years)

        # 4. Project Relevance Score
        proj_score = self._compute_project_relevance(resume, jd)

        return MatchResult(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            extra_skills=extra_skills,
            category_breakdown=category_breakdown,
            keyword_similarity=round(keyword_similarity, 2),
            top_matching_keywords=top_matching_keywords,
            missing_critical_keywords=missing_critical_keywords,
            skill_match_percentage=round(skill_match_percentage, 1),
            experience_match_score=round(exp_score, 1),
            project_relevance_score=round(proj_score, 1),
            jd_min_exp=jd.min_experience_years,
            candidate_exp=resume.experience_years
        )

    def _compute_keyword_similarity(self, text_a: str, text_b: str) -> Tuple[float, List[Tuple[str, float]]]:
        """Calculates cosine similarity of TF-IDF representations."""
        if not text_a or not text_b:
            return 0.0, []

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=100
            )
            tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
            cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            # Find top shared features
            feature_names = np.array(vectorizer.get_feature_names_out())
            prod = tfidf_matrix[0].toarray() * tfidf_matrix[1].toarray()
            top_indices = np.argsort(prod[0])[::-1]

            shared_keywords = []
            for idx in top_indices:
                score = prod[0][idx]
                if score > 0:
                    shared_keywords.append((str(feature_names[idx]), float(round(score * 100, 1))))
                if len(shared_keywords) >= 10:
                    break

            return float(cos_sim * 100.0), shared_keywords
        except Exception:
            return 0.0, []

    def _compute_experience_score(self, candidate_years: float, required_years: float) -> float:
        """
        Calculates experience compatibility (0-100).
        If candidate meets or exceeds requirement, award full 100.
        If requirement is 0, award full 100.
        """
        if required_years <= 0:
            return 100.0 if candidate_years > 0 else 80.0

        if candidate_years >= required_years:
            return 100.0

        # Partial credit proportional to required years
        ratio = candidate_years / required_years
        return min(100.0, max(15.0, ratio * 100.0))

    def _compute_project_relevance(self, resume: ResumeData, jd: JobDescriptionData) -> float:
        """
        Calculates project relevance based on skills demonstrated in projects vs JD.
        """
        if not resume.projects:
            # If no explicit projects section, fallback to overall skill overlap
            return min(100.0, len(resume.skills) * 8.0)

        # Aggregate project text
        project_text = " ".join(
            p.get("title", "") + " " + p.get("details", "") + " " + " ".join(p.get("bullets", []))
            for p in resume.projects
        )

        # Check overlap of JD skills in projects
        if not jd.skills:
            return 80.0

        matched_in_projects = sum(
            1 for s in jd.skills if re.search(r"\b" + re.escape(s) + r"\b", project_text, re.IGNORECASE)
        )
        ratio = (matched_in_projects / len(jd.skills)) * 100.0

        # Base score on projects count and skill relevance
        project_count_boost = min(30.0, len(resume.projects) * 10.0)
        relevance = min(100.0, (ratio * 0.7) + project_count_boost)
        return max(20.0, relevance)
