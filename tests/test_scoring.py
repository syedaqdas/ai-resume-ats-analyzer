"""
Unit tests for ATS Score Calculation engine and weight validation.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyzer.ats_score import ATSScoreCalculator, ATSScoreReport
from analyzer.matcher import MatchResult


class TestATSScoring:
    """Tests for ATS scoring formula, weight enforcement, and edge cases."""

    @pytest.fixture
    def calculator(self):
        return ATSScoreCalculator()

    def test_perfect_score(self, calculator):
        match = MatchResult(
            skill_match_percentage=100.0,
            keyword_similarity=100.0,
            experience_match_score=100.0,
            project_relevance_score=100.0,
            matched_skills=["Python", "AWS"],
            missing_skills=[]
        )
        report = calculator.calculate(match)

        assert report.total_score == 100
        assert report.grade == "Excellent Match"
        assert report.status_color == "#10B981"
        assert report.skills_score == 100.0
        assert report.keyword_score == 100.0
        assert report.experience_score == 100.0
        assert report.project_score == 100.0

    def test_zero_score(self, calculator):
        match = MatchResult(
            skill_match_percentage=0.0,
            keyword_similarity=0.0,
            experience_match_score=0.0,
            project_relevance_score=0.0,
            matched_skills=[],
            missing_skills=["Python", "Docker"]
        )
        report = calculator.calculate(match)

        assert report.total_score == 0
        assert report.grade == "Needs Improvement"
        assert report.status_color == "#EF4444"

    def test_weight_enforcement(self, calculator):
        """
        Validates individual weight contributions:
        Skills: 40%
        Keywords: 25%
        Experience: 20%
        Projects: 15%
        """
        # 1. 100% Skills only
        match_skills_only = MatchResult(
            skill_match_percentage=100.0,
            keyword_similarity=0.0,
            experience_match_score=0.0,
            project_relevance_score=0.0
        )
        assert calculator.calculate(match_skills_only).total_score == 40

        # 2. 100% Keywords only
        match_kw_only = MatchResult(
            skill_match_percentage=0.0,
            keyword_similarity=100.0,
            experience_match_score=0.0,
            project_relevance_score=0.0
        )
        assert calculator.calculate(match_kw_only).total_score == 25

        # 3. 100% Experience only
        match_exp_only = MatchResult(
            skill_match_percentage=0.0,
            keyword_similarity=0.0,
            experience_match_score=100.0,
            project_relevance_score=0.0
        )
        assert calculator.calculate(match_exp_only).total_score == 20

        # 4. 100% Projects only
        match_proj_only = MatchResult(
            skill_match_percentage=0.0,
            keyword_similarity=0.0,
            experience_match_score=0.0,
            project_relevance_score=100.0
        )
        assert calculator.calculate(match_proj_only).total_score == 15

    def test_grade_classifications(self, calculator):
        # 87 points -> Excellent Match
        match_87 = MatchResult(
            skill_match_percentage=90.0,   # 36.0
            keyword_similarity=80.0,       # 20.0
            experience_match_score=90.0,   # 18.0
            project_relevance_score=85.0   # 12.75 -> Total = 86.75 -> 87
        )
        report = calculator.calculate(match_87)
        assert report.total_score == 87
        assert report.grade == "Excellent Match"

        # 75 points -> Good Match
        match_75 = MatchResult(
            skill_match_percentage=75.0,
            keyword_similarity=75.0,
            experience_match_score=75.0,
            project_relevance_score=75.0
        )
        report_75 = calculator.calculate(match_75)
        assert report_75.total_score == 75
        assert report_75.grade == "Good Match"

        # 60 points -> Moderate Match
        match_60 = MatchResult(
            skill_match_percentage=60.0,
            keyword_similarity=60.0,
            experience_match_score=60.0,
            project_relevance_score=60.0
        )
        report_60 = calculator.calculate(match_60)
        assert report_60.total_score == 60
        assert report_60.grade == "Moderate Match"

    def test_clamping_behavior(self, calculator):
        """Values over 100 or under 0 should be gracefully clamped."""
        match_overflow = MatchResult(
            skill_match_percentage=150.0,
            keyword_similarity=120.0,
            experience_match_score=200.0,
            project_relevance_score=110.0
        )
        report = calculator.calculate(match_overflow)
        assert report.total_score == 100

        match_underflow = MatchResult(
            skill_match_percentage=-20.0,
            keyword_similarity=-10.0,
            experience_match_score=-5.0,
            project_relevance_score=-15.0
        )
        report_under = calculator.calculate(match_underflow)
        assert report_under.total_score == 0
