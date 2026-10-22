"""
ATS Score Engine for AI Resume ATS Analyzer.
Calculates weighted composite ATS score (Skills 40%, Keywords 25%,
Experience 20%, Projects 15%) and generates actionable performance diagnostics.
"""

from dataclasses import dataclass, field
from typing import Dict, List
from analyzer.matcher import MatchResult


@dataclass
class ATSScoreReport:
    """Encapsulates the complete ATS evaluation breakdown."""
    total_score: int
    grade: str
    status_color: str
    skills_score: float
    keyword_score: float
    experience_score: float
    project_score: float
    weighted_breakdown: Dict[str, Dict[str, float]]
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    detailed_explanation: str = ""


class ATSScoreCalculator:
    """
    Computes weighted ATS compatibility score strictly adhering to the specification:
    - Skills Match: 40%
    - Keyword Match: 25%
    - Experience Match: 20%
    - Project Relevance: 15%
    """

    WEIGHTS = {
        "skills": 0.40,
        "keywords": 0.25,
        "experience": 0.20,
        "projects": 0.15
    }

    def calculate(self, match_result: MatchResult) -> ATSScoreReport:
        """
        Calculates composite ATS score from match metrics and returns ATSScoreReport.
        """
        skills_score = min(100.0, max(0.0, match_result.skill_match_percentage))
        keyword_score = min(100.0, max(0.0, match_result.keyword_similarity))
        exp_score = min(100.0, max(0.0, match_result.experience_match_score))
        proj_score = min(100.0, max(0.0, match_result.project_relevance_score))

        # Weighted contributions
        skills_contrib = skills_score * self.WEIGHTS["skills"]
        keyword_contrib = keyword_score * self.WEIGHTS["keywords"]
        exp_contrib = exp_score * self.WEIGHTS["experience"]
        proj_contrib = proj_score * self.WEIGHTS["projects"]

        raw_total = skills_contrib + keyword_contrib + exp_contrib + proj_contrib
        total_score = int(round(raw_total))
        # Ensure within bounds [0, 100]
        total_score = max(0, min(100, total_score))

        # Determine grade and color
        if total_score >= 85:
            grade = "Excellent Match"
            status_color = "#10B981"  # Emerald Green
        elif total_score >= 70:
            grade = "Good Match"
            status_color = "#3B82F6"  # Royal Blue
        elif total_score >= 50:
            grade = "Moderate Match"
            status_color = "#F59E0B"  # Amber Orange
        else:
            grade = "Needs Improvement"
            status_color = "#EF4444"  # Coral Red

        # Build diagnostic strengths and weaknesses
        strengths = []
        weaknesses = []

        if skills_score >= 75:
            strengths.append(f"Strong skill alignment: {len(match_result.matched_skills)} required technical skills matched ({skills_score:.0f}%).")
        else:
            weaknesses.append(f"Skill gaps identified: Missing {len(match_result.missing_skills)} required technical skills.")

        if keyword_score >= 50:
            strengths.append(f"Solid semantic and keyword resonance with job description ({keyword_score:.1f}%).")
        else:
            weaknesses.append("Low keyword density: Resume lacks industry keywords and phrasing used in the job description.")

        if exp_score >= 90:
            strengths.append(f"Experience level aligns with requirement ({match_result.candidate_exp} yrs vs {match_result.jd_min_exp} yrs required).")
        else:
            weaknesses.append(f"Experience shortfall: Candidate has {match_result.candidate_exp} yrs vs {match_result.jd_min_exp} yrs requested.")

        if proj_score >= 70:
            strengths.append("Project descriptions demonstrate relevant technologies and tools.")
        else:
            weaknesses.append("Projects section needs deeper alignment with the core tech stack requested.")

        # Build detailed explanation
        detailed_explanation = (
            f"Your resume achieved an ATS Compatibility Score of {total_score}/100 ({grade}). "
            f"Technical skills contributed {skills_contrib:.1f}/40 pts, keyword density contributed "
            f"{keyword_contrib:.1f}/25 pts, professional experience added {exp_contrib:.1f}/20 pts, "
            f"and project alignment provided {proj_contrib:.1f}/15 pts. "
        )
        if weaknesses:
            detailed_explanation += f"To increase your score, focus on: {weaknesses[0]}"

        weighted_breakdown = {
            "Skills Match (40%)": {
                "score": round(skills_score, 1),
                "weight": 0.40,
                "contribution": round(skills_contrib, 1),
                "max_points": 40.0
            },
            "Keyword Match (25%)": {
                "score": round(keyword_score, 1),
                "weight": 0.25,
                "contribution": round(keyword_contrib, 1),
                "max_points": 25.0
            },
            "Experience Match (20%)": {
                "score": round(exp_score, 1),
                "weight": 0.20,
                "contribution": round(exp_contrib, 1),
                "max_points": 20.0
            },
            "Project Relevance (15%)": {
                "score": round(proj_score, 1),
                "weight": 0.15,
                "contribution": round(proj_contrib, 1),
                "max_points": 15.0
            }
        }

        return ATSScoreReport(
            total_score=total_score,
            grade=grade,
            status_color=status_color,
            skills_score=round(skills_score, 1),
            keyword_score=round(keyword_score, 1),
            experience_score=round(exp_score, 1),
            project_score=round(proj_score, 1),
            weighted_breakdown=weighted_breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            detailed_explanation=detailed_explanation
        )
