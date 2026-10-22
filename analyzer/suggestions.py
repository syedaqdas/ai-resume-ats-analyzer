"""
Resume Improvement Suggestions Generator for AI Resume ATS Analyzer.
Analyzes bullet points, identifies weak action verbs, flags missing metrics,
recommends keyword optimization, and generates Before/After rewrite pairs.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from analyzer.resume_parser import ResumeData
from analyzer.matcher import MatchResult


@dataclass
class RewriteSuggestion:
    """Represents a concrete Before/After bullet point rewrite recommendation."""
    original: str
    suggested: str
    reason: str
    weak_phrase: Optional[str] = None
    technologies_added: List[str] = field(default_factory=list)


@dataclass
class SectionAudit:
    """Audit of resume structural components."""
    section_name: str
    is_present: bool
    status: str
    recommendation: str


@dataclass
class SuggestionsReport:
    """Collection of all improvement suggestions across categories."""
    bullet_rewrites: List[RewriteSuggestion] = field(default_factory=list)
    weak_verbs_found: List[str] = field(default_factory=list)
    missing_metrics_count: int = 0
    total_bullets_analyzed: int = 0
    keyword_placement_tips: List[str] = field(default_factory=list)
    project_enhancement_tips: List[str] = field(default_factory=list)
    structural_audits: List[SectionAudit] = field(default_factory=list)
    general_recommendations: List[str] = field(default_factory=list)


# Mapping of weak phrasing to strong action verbs and templates
WEAK_PHRASE_MAPPING = {
    "worked on": ["Architected", "Engineered", "Developed", "Spearheaded", "Implemented"],
    "was responsible for": ["Orchestrated", "Directed", "Executed", "Administered"],
    "responsible for": ["Led", "Managed", "Orchestrated", "Governed"],
    "helped with": ["Collaborated to deliver", "Co-engineered", "Facilitated"],
    "assisted in": ["Partnered to build", "Contributed to developing", "Accelerated"],
    "handled": ["Managed", "Resolved", "Streamlined", "Optimized"],
    "did": ["Executed", "Conducted", "Implemented"],
    "involved in": ["Collaborated across", "Drove the implementation of"],
    "participated in": ["Co-led the delivery of", "Actively contributed to engineering"],
    "tried to": ["Initiated", "Piloted", "Executed"],
    "looked after": ["Oversaw", "Maintained", "Safeguarded"]
}


class SuggestionsGenerator:
    """Generates targeted, high-impact resume improvement suggestions."""

    def generate(self, resume: ResumeData, match_result: MatchResult) -> SuggestionsReport:
        """
        Runs comprehensive diagnosis on resume content and job description match.
        """
        rewrites: List[RewriteSuggestion] = []
        weak_verbs_detected = set()
        missing_metrics_count = 0

        # Available missing skills to sprinkle into suggested rewrites
        available_missing_skills = match_result.missing_skills.copy()

        # 1. Analyze bullet points from resume
        for bp in resume.bullet_points:
            text = bp.text
            lower_text = text.lower()

            if not bp.has_metric:
                missing_metrics_count += 1

            # Check for weak phrasing
            matched_weak = None
            for weak_key in WEAK_PHRASE_MAPPING:
                if weak_key in lower_text:
                    matched_weak = weak_key
                    weak_verbs_detected.add(weak_key)
                    break

            # If bullet has weak phrasing OR lacks both strong verb and metrics, suggest rewrite
            if matched_weak or (not bp.starts_with_action_verb and not bp.has_metric):
                rewrite = self._generate_bullet_rewrite(
                    text, matched_weak, bp.has_metric, available_missing_skills
                )
                if rewrite:
                    rewrites.append(rewrite)
                if len(rewrites) >= 5:
                    break

        # Fallback if no bullet points met rewrite criteria
        if not rewrites and resume.bullet_points:
            # Pick first 2 bullets and show how to add metrics and action verbs
            for bp in resume.bullet_points[:2]:
                rewrite = self._generate_bullet_rewrite(
                    bp.text, None, bp.has_metric, available_missing_skills
                )
                if rewrite:
                    rewrites.append(rewrite)

        # 2. Keyword placement suggestions
        keyword_tips = self._generate_keyword_tips(match_result)

        # 3. Project enhancement tips
        project_tips = self._generate_project_tips(resume, match_result)

        # 4. Structural checklist audit
        structural_audits = self._audit_structure(resume)

        # 5. General recommendations
        general_recommendations = self._generate_general_recommendations(
            resume, match_result, missing_metrics_count, len(resume.bullet_points)
        )

        return SuggestionsReport(
            bullet_rewrites=rewrites,
            weak_verbs_found=sorted(list(weak_verbs_detected)),
            missing_metrics_count=missing_metrics_count,
            total_bullets_analyzed=len(resume.bullet_points),
            keyword_placement_tips=keyword_tips,
            project_enhancement_tips=project_tips,
            structural_audits=structural_audits,
            general_recommendations=general_recommendations
        )

    def _generate_bullet_rewrite(
        self,
        original: str,
        weak_phrase: Optional[str],
        has_metric: bool,
        missing_skills: List[str]
    ) -> Optional[RewriteSuggestion]:
        """Generates an enhanced Before/After rewrite for a bullet point."""
        text_clean = original.strip().lstrip("-*• ")
        words = text_clean.split()
        if len(words) < 3:
            return None

        # Determine replacement verb
        replacement_verb = "Engineered"
        if weak_phrase and weak_phrase in WEAK_PHRASE_MAPPING:
            replacement_verb = WEAK_PHRASE_MAPPING[weak_phrase][0]
        elif not words[0].lower().endswith("ed"):
            replacement_verb = "Developed"

        # Formulate core rewritten sentence
        cleaned_core = text_clean
        if weak_phrase:
            # Replace the weak phrase
            pattern = re.compile(re.escape(weak_phrase), re.IGNORECASE)
            cleaned_core = pattern.sub(replacement_verb, text_clean, count=1)
        else:
            # Prepend or swap initial word
            if words[0].lower() in ["i", "the", "a", "an", "to"]:
                cleaned_core = f"{replacement_verb} " + " ".join(words[1:])
            else:
                cleaned_core = f"{replacement_verb} " + text_clean

        # Clean punctuation
        cleaned_core = cleaned_core.rstrip(". ")

        # Add quantifiable impact metric if missing
        impact_phrases = [
            ", improving processing throughput by 32% and reducing latency.",
            ", boosting user engagement by 25% and system reliability.",
            ", resulting in a 40% reduction in deployment time.",
            ", scaling capacity to handle 100K+ daily transactions."
        ]
        # Deterministically select metric based on hash
        metric_addition = impact_phrases[len(original) % len(impact_phrases)]

        suggested = cleaned_core + metric_addition
        reason = "Replaced passive phrasing with a strong dynamic action verb and quantified impact with measurable metrics."

        return RewriteSuggestion(
            original=text_clean,
            suggested=suggested,
            reason=reason,
            weak_phrase=weak_phrase
        )

    def _generate_keyword_tips(self, match: MatchResult) -> List[str]:
        """Generates targeted keyword placement recommendations."""
        tips = []
        if match.missing_skills:
            top_missing = match.missing_skills[:5]
            tips.append(
                f"**Integrate Missing Skills:** Explicitly add `{', '.join(top_missing)}` into your Technical Skills section "
                "under their appropriate category headings."
            )
            tips.append(
                f"**Contextualize in Experience:** Don't just list `{top_missing[0]}` in a list; reference it inside an Experience "
                f"bullet point (e.g. *'Leveraged {top_missing[0]} to streamline automated workflows...'*) so ATS context-parsers score it."
            )

        if match.missing_critical_keywords:
            top_kw = match.missing_critical_keywords[:4]
            tips.append(
                f"**Adopt Job Description Buzzwords:** Weave matching keywords like `{', '.join(top_kw)}` into your "
                "Professional Summary and work descriptions to maximize TF-IDF resonance."
            )

        if not tips:
            tips.append("Excellent keyword coverage! Your resume mirrors the target job description's core terminology.")

        return tips

    def _generate_project_tips(self, resume: ResumeData, match: MatchResult) -> List[str]:
        """Generates project description enhancement advice."""
        tips = [
            "**Adopt the STAR Method:** Structure every project entry as: **S**ituation (problem context), "
            "**T**ask (objective), **A**ction (technologies & architecture implemented), and **R**esult (quantifiable metrics).",
            "**Explicit Tech Stack Line:** Add a clear `Tech Stack: ...` line to each project entry "
            "(e.g., *'Technologies: Python, FastAPI, Docker, PostgreSQL'*). This guarantees immediate ATS token matching.",
            "**Include Public Repositories:** Add direct links to live demos or GitHub repositories. "
            "ATS systems and technical recruiters heavily favor candidates with verifiable code."
        ]

        if match.missing_skills:
            tips.append(
                f"**Showcase Missing Tech in Projects:** If you have hobby or side-project experience with "
                f"`{match.missing_skills[0]}`, add a dedicated project showcasing it."
            )

        return tips

    def _audit_structure(self, resume: ResumeData) -> List[SectionAudit]:
        """Audits structural integrity and ATS standard readability."""
        audits = []

        # 1. Contact Information
        has_contact = bool(resume.email and resume.phone)
        audits.append(SectionAudit(
            section_name="Contact Information",
            is_present=has_contact,
            status="Complete" if has_contact else "Incomplete",
            recommendation="Include full name, professional email, phone number, and LinkedIn URL at the top." if not has_contact else "Contact details are complete and easily accessible to ATS scrapers."
        ))

        # 2. Professional Summary
        has_summary = bool(resume.sections.get("summary"))
        audits.append(SectionAudit(
            section_name="Professional Summary",
            is_present=has_summary,
            status="Present" if has_summary else "Missing / Blended",
            recommendation="Add a 3-4 sentence professional summary highlighting your core expertise, years of experience, and primary tech stack." if not has_summary else "Summary section clearly outlines professional value proposition."
        ))

        # 3. Work Experience
        has_exp = bool(resume.sections.get("experience") or resume.experience_entries)
        audits.append(SectionAudit(
            section_name="Work Experience",
            is_present=has_exp,
            status="Present" if has_exp else "Needs Attention",
            recommendation="Format experience with reverse-chronological dates (e.g. 2021 - Present), company names, job titles, and bullet points." if not has_exp else "Work experience section is properly structured."
        ))

        # 4. Technical Skills
        has_skills = bool(len(resume.skills) >= 5)
        audits.append(SectionAudit(
            section_name="Technical Skills",
            is_present=has_skills,
            status=f"Strong ({len(resume.skills)} skills)" if has_skills else "Thin",
            recommendation="Organize skills into labeled categories (Languages, Frameworks, Cloud, Databases) rather than an unorganized comma-separated list." if not has_skills else "Well-populated technical skills section."
        ))

        # 5. Education
        has_edu = bool(resume.education)
        audits.append(SectionAudit(
            section_name="Education",
            is_present=has_edu,
            status="Present" if has_edu else "Missing",
            recommendation="Include degree title, field of study, institution name, and graduation year." if not has_edu else "Education section identified."
        ))

        return audits

    def _generate_general_recommendations(
        self,
        resume: ResumeData,
        match: MatchResult,
        missing_metrics_count: int,
        total_bullets: int
    ) -> List[str]:
        """Provides high-level actionable takeaways."""
        recs = []
        if total_bullets > 0 and (missing_metrics_count / total_bullets) > 0.4:
            pct_missing = int((missing_metrics_count / total_bullets) * 100)
            recs.append(
                f"**Add Quantifiable Metrics:** {pct_missing}% of your bullet points currently lack measurable numbers. "
                "Include percentage improvements, latency drops, dollar amounts, team sizes, or scale."
            )

        if match.skill_match_percentage < 70.0:
            recs.append(
                f"**Close the Skill Gap:** Your skill match is currently {match.skill_match_percentage:.0f}%. "
                f"Review the {len(match.missing_skills)} missing skills and include those you possess."
            )

        if not resume.links.get("linkedin"):
            recs.append("**Include LinkedIn Profile:** Modern ATS platforms index LinkedIn URLs to verify candidate background.")

        recs.append(
            "**Single-Column Layout:** Avoid multi-column or heavily formatted graphical resumes. "
            "Clean standard single-column text ensures 100% parse rate across older enterprise ATS systems (Workday, Taleo, iCIMS)."
        )

        return recs
