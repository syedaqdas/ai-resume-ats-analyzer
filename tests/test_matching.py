"""
Unit tests for Skill Extraction, Job Matching, and Improvement Suggestions.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer.skill_extractor import SkillExtractor
from analyzer.matcher import JobDescriptionParser, ResumeMatcher
from analyzer.resume_parser import ResumeParser
from analyzer.suggestions import SuggestionsGenerator
from utils.helpers import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS


class TestSkillExtractor:
    """Tests for skill matching, boundary handling, and alias resolution."""

    @pytest.fixture
    def extractor(self):
        return SkillExtractor()

    def test_basic_skill_extraction(self, extractor):
        text = "I am proficient in Python, SQL, and Docker containerization."
        skills, categorized, freqs = extractor.extract_skills(text)

        assert "Python" in skills
        assert "SQL" in skills
        assert "Docker" in skills
        assert freqs["Python"] >= 1

    def test_boundary_handling_and_special_symbols(self, extractor):
        """Ensure C++, C#, Go, and SQL don't produce false positive matches."""
        # 'Good' or 'Going' shouldn't match 'Go'
        text_no_go = "We are going to have a good time with MongoDB."
        skills, _, _ = extractor.extract_skills(text_no_go)
        assert "Go" not in skills
        assert "MongoDB" in skills

        # 'Go' by itself should match
        text_go = "We write backend services in Go and C++."
        skills_go, _, _ = extractor.extract_skills(text_go)
        assert "Go" in skills_go
        assert "C++" in skills_go

        # 'C#' matching
        text_csharp = "Enterprise desktop apps built with C# and .NET Core."
        skills_csharp, _, _ = extractor.extract_skills(text_csharp)
        assert "C#" in skills_csharp

    def test_alias_normalization(self, extractor):
        """Aliases like k8s, reactjs, and sklearn should normalize to canonical names."""
        text = "Deployed k8s clusters, built frontend in reactjs, trained models with sklearn and tf."
        skills, _, _ = extractor.extract_skills(text)

        assert "Kubernetes" in skills
        assert "React" in skills
        assert "Scikit-learn" in skills
        assert "TensorFlow" in skills

    def test_multi_word_skills(self, extractor):
        text = "Skilled in Machine Learning, Natural Language Processing, REST API, and Spring Boot."
        skills, _, _ = extractor.extract_skills(text)

        assert "Machine Learning" in skills
        assert "NLP" in skills or "Natural Language Processing" in skills
        assert "REST API" in skills
        assert "Spring Boot" in skills


class TestJobDescriptionParser:
    """Tests for parsing job descriptions and extracting requirements."""

    @pytest.fixture
    def parser(self):
        return JobDescriptionParser()

    def test_experience_extraction_range(self, parser):
        text = "Looking for a Software Engineer with 3-5 years of experience in Python."
        jd = parser.parse(text)
        assert jd.min_experience_years == 3.0
        assert jd.max_experience_years == 5.0
        assert "Python" in jd.skills

    def test_experience_extraction_plus(self, parser):
        text = "Requirements: 5+ years of experience building cloud systems."
        jd = parser.parse(text)
        assert jd.min_experience_years == 5.0

    def test_education_extraction(self, parser):
        text = "Must possess a Bachelor's or Master's degree in Computer Science."
        jd = parser.parse(text)
        assert "Bachelor's" in jd.required_education
        assert "Master's" in jd.required_education


class TestResumeMatcher:
    """Tests for matching logic between resume and job description."""

    @pytest.fixture
    def resume_parser(self):
        return ResumeParser()

    @pytest.fixture
    def jd_parser(self):
        return JobDescriptionParser()

    @pytest.fixture
    def matcher(self):
        return ResumeMatcher()

    def test_matching_pipeline(self, resume_parser, jd_parser, matcher):
        resume_text = SAMPLE_RESUMES["AI / ML Engineer"]
        jd_text = SAMPLE_JOB_DESCRIPTIONS["Senior Machine Learning Engineer"]

        resume = resume_parser.parse(resume_text)
        jd = jd_parser.parse(jd_text)
        match = matcher.match(resume, jd)

        # Matched skills
        assert len(match.matched_skills) > 0
        assert "Python" in match.matched_skills
        assert "PyTorch" in match.matched_skills
        assert "Kubernetes" in match.matched_skills

        # Skill percentage should be reasonably high
        assert match.skill_match_percentage >= 50.0

        # Cosine similarity should be positive
        assert match.keyword_similarity > 20.0

        # Experience score
        assert match.experience_match_score >= 80.0


class TestSuggestionsGenerator:
    """Tests for weak action verb detection and Before/After rewrites."""

    def test_weak_verb_replacement(self):
        generator = SuggestionsGenerator()
        resume_parser = ResumeParser()
        jd_parser = JobDescriptionParser()
        matcher = ResumeMatcher()

        resume_text = """
        John Smith
        john@example.com | 555-123-4567

        EXPERIENCE
        Developer | ACME Corp | 2021 - Present
        - Worked on web application using Python and React.
        - Responsible for database backups and server monitoring.
        - Helped with client API integrations.
        """
        jd_text = "Looking for Senior Engineer with Python, React, Docker, and AWS."

        resume = resume_parser.parse(resume_text)
        jd = jd_parser.parse(jd_text)
        match = matcher.match(resume, jd)
        suggestions = generator.generate(resume, match)

        assert len(suggestions.weak_verbs_found) >= 2
        assert any("worked on" in v for v in suggestions.weak_verbs_found)
        assert len(suggestions.bullet_rewrites) >= 1

        # Check Before / After rewrite quality
        first_rewrite = suggestions.bullet_rewrites[0]
        assert "Worked on" in first_rewrite.original
        # After should contain strong power verb and metric
        assert first_rewrite.suggested != first_rewrite.original
        assert any(metric in first_rewrite.suggested for metric in ["%", "throughput", "latency", "capacity"])

        # Check structural audits
        assert len(suggestions.structural_audits) >= 4
