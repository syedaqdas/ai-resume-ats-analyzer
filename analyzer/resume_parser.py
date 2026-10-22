"""
Resume Parser module for AI Resume ATS Analyzer.
Extracts contact info, candidate name, education, work experience, projects,
and certifications from resume text.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from utils.helpers import (
    clean_text,
    extract_email,
    extract_links,
    extract_phone,
    extract_sections
)
from analyzer.skill_extractor import SkillExtractor, get_nlp


@dataclass
class BulletPointAnalysis:
    """Analysis of a single bullet point or experience sentence."""
    text: str
    has_action_verb: bool
    starts_with_action_verb: bool
    action_verb: Optional[str]
    has_metric: bool
    metrics_found: List[str]
    word_count: int


@dataclass
class ResumeData:
    """Structured representation of parsed resume data."""
    raw_text: str
    cleaned_text: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    links: Dict[str, Optional[str]] = field(default_factory=dict)
    skills: List[str] = field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = field(default_factory=dict)
    skill_frequencies: Dict[str, int] = field(default_factory=dict)
    education: List[Dict[str, str]] = field(default_factory=list)
    experience_years: float = 0.0
    experience_entries: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    sections: Dict[str, str] = field(default_factory=dict)
    bullet_points: List[BulletPointAnalysis] = field(default_factory=list)


# Action verbs database (strong dynamic verbs)
ACTION_VERBS = {
    "architected", "engineered", "developed", "designed", "spearheaded",
    "implemented", "orchestrated", "deployed", "scaled", "optimized",
    "automated", "built", "created", "constructed", "led", "mentored",
    "managed", "accelerated", "boosted", "delivered", "established",
    "formulated", "generated", "improved", "increased", "reduced",
    "refactored", "resolved", "streamlined", "transformed", "directed",
    "authored", "launched", "executed", "initiated", "pioneered"
}

# Weak/passive action verbs
WEAK_VERBS = {
    "worked", "worked on", "responsible for", "assisted", "helped",
    "participated", "involved in", "did", "handled", "tried",
    "attempted", "contributed to", "supported", "tasked with"
}


class ResumeParser:
    """
    Parses resume text into structured fields using spaCy NER,
    regular expressions, and heuristics.
    """

    def __init__(self):
        self.skill_extractor = SkillExtractor()

    def parse(self, raw_text: str) -> ResumeData:
        """
        Parses raw resume text into a comprehensive ResumeData object.
        """
        cleaned = clean_text(raw_text)
        sections = extract_sections(cleaned)

        # 1. Contact Information
        email = extract_email(cleaned)
        phone = extract_phone(cleaned)
        links = extract_links(cleaned)

        # 2. Candidate Name
        name = self._extract_name(cleaned, sections.get("header", ""))

        # 3. Skills
        skills, categorized, freqs = self.skill_extractor.extract_skills(cleaned)

        # 4. Education
        education = self._extract_education(sections.get("education", "") or cleaned)

        # 5. Experience and Years
        exp_text = sections.get("experience", "") or cleaned
        experience_years, exp_entries = self._extract_experience(exp_text)

        # 6. Projects
        proj_text = sections.get("projects", "")
        projects = self._extract_projects(proj_text, cleaned)

        # 7. Certifications
        cert_text = sections.get("certifications", "")
        certifications = self._extract_certifications(cert_text, cleaned)

        # 8. Bullet points analysis
        bullet_points = self._analyze_bullet_points(exp_text + "\n" + proj_text)

        return ResumeData(
            raw_text=raw_text,
            cleaned_text=cleaned,
            name=name,
            email=email,
            phone=phone,
            links=links,
            skills=skills,
            categorized_skills=categorized,
            skill_frequencies=freqs,
            education=education,
            experience_years=experience_years,
            experience_entries=exp_entries,
            projects=projects,
            certifications=certifications,
            sections=sections,
            bullet_points=bullet_points
        )

    def _extract_name(self, full_text: str, header_text: str) -> Optional[str]:
        """
        Extracts candidate name using spaCy NER, fallback to top line heuristics.
        """
        # Look at the first 5 lines of resume
        lines = [line.strip() for line in full_text.splitlines() if line.strip()][:5]
        if not lines:
            return None

        # Exclude lines with email, phone, links, or headers
        candidate_lines = []
        for line in lines:
            if "@" in line or "http" in line or "www." in line or "linkedin" in line:
                continue
            if re.search(r"\b(?:resume|curriculum vitae|cv|summary|profile|page)\b", line, re.IGNORECASE):
                continue
            candidate_lines.append(line)

        # Try spaCy NER on candidate lines
        nlp = get_nlp()
        for cand in candidate_lines:
            doc = nlp(cand)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                    return ent.text.strip()

        # Heuristic fallback: First non-contact line with 2-4 capitalized words
        for cand in candidate_lines:
            words = cand.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                return cand.strip()

        # If header text exists, first word line
        if candidate_lines:
            return candidate_lines[0].strip()

        return None

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts degree level, field, university, and graduation year.
        """
        education_records = []
        degree_patterns = [
            r"\b(?:Ph\.?D|Doctor of Philosophy)\b",
            r"\b(?:M\.?S|M\.?Sc|Master of Science|Master of Arts|M\.?A|Master's|MBA)\b",
            r"\b(?:B\.?S|B\.?Sc|Bachelor of Science|Bachelor of Arts|B\.?A|B\.?Tech|B\.?E|Bachelor's)\b",
            r"\b(?:Associate of (?:Science|Arts)|Associate Degree)\b"
        ]

        lines = text.splitlines()
        for line in lines:
            matched_degree = None
            for pat in degree_patterns:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    matched_degree = m.group(0)
                    break

            if matched_degree:
                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", line)
                year = year_match.group(0) if year_match else "N/A"
                education_records.append({
                    "degree": matched_degree,
                    "raw_line": line.strip(),
                    "year": year
                })

        return education_records

    def _extract_experience(self, text: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculates estimated total experience years from date ranges (e.g. 2018 - 2022, 2021 - Present).
        """
        current_year = datetime.now().year
        # Pattern for year ranges: 2018 - 2022 or 2020 - Present
        range_pattern = r"\b(19\d{2}|20\d{2})\s*(?:-|–|to)\s*(19\d{2}|20\d{2}|present|current)\b"
        matches = re.findall(range_pattern, text, re.IGNORECASE)

        total_years = 0.0
        intervals = []
        entries = []

        for start_str, end_str in matches:
            start_yr = int(start_str)
            if end_str.lower() in ["present", "current"]:
                end_yr = current_year
            else:
                end_yr = int(end_str)

            if 1970 <= start_yr <= current_year and end_yr >= start_yr:
                span = max(1, end_yr - start_yr)
                intervals.append((start_yr, end_yr))
                entries.append({
                    "start": start_yr,
                    "end": end_yr if end_str.lower() not in ["present", "current"] else "Present",
                    "years": span
                })

        # Check explicit mentions like "5+ years of experience"
        mention_pattern = r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)(?:\s+of)?\s+experience"
        explicit_matches = re.findall(mention_pattern, text, re.IGNORECASE)
        explicit_years = [float(y) for y in explicit_matches if float(y) < 40]

        if intervals:
            # Merge overlapping intervals to avoid double counting
            intervals.sort(key=lambda x: x[0])
            merged = [intervals[0]]
            for current in intervals[1:]:
                prev_start, prev_end = merged[-1]
                if current[0] <= prev_end:
                    merged[-1] = (prev_start, max(prev_end, current[1]))
                else:
                    merged.append(current)
            interval_years = sum(end - start for start, end in merged)
            total_years = float(interval_years)
        elif explicit_years:
            total_years = max(explicit_years)
        else:
            total_years = 0.0

        # If explicit statement gives higher experience, prefer it
        if explicit_years and max(explicit_years) > total_years:
            total_years = max(explicit_years)

        return round(total_years, 1), entries

    def _extract_projects(self, proj_text: str, full_text: str) -> List[Dict[str, Any]]:
        """
        Extracts project titles, descriptions, and technologies.
        """
        source = proj_text if proj_text else full_text
        projects = []

        lines = source.splitlines()
        current_project = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Identify project headers like: Project Name | Tech: Python, React
            if ("|" in line_str or ":" in line_str) and len(line_str.split()) <= 10 and not line_str.startswith("*"):
                if current_project:
                    projects.append(current_project)
                parts = re.split(r"[:|]", line_str)
                title = parts[0].strip()
                current_project = {
                    "title": title,
                    "details": line_str,
                    "bullets": []
                }
            elif current_project and (line_str.startswith(("-", "*", "•")) or len(line_str) > 20):
                current_project["bullets"].append(line_str.lstrip("-*• "))

        if current_project:
            projects.append(current_project)

        return projects[:6]  # Return up to top 6 projects

    def _extract_certifications(self, cert_text: str, full_text: str) -> List[str]:
        """
        Extracts certifications listed in the resume.
        """
        source = cert_text if cert_text else full_text
        cert_keywords = [
            "AWS Certified", "Azure", "Google Cloud", "GCP", "Kubernetes",
            "CKA", "CKAD", "PMP", "CompTIA", "CISSP", "Scrum Master",
            "Specialization", "Professional Certificate", "Certified"
        ]

        found_certs = []
        for line in source.splitlines():
            line_clean = line.strip()
            if any(k.lower() in line_clean.lower() for k in cert_keywords):
                if len(line_clean) < 120 and not line_clean.lower().startswith("education"):
                    cleaned_cert = line_clean.lstrip("-*• ")
                    if cleaned_cert and cleaned_cert not in found_certs:
                        found_certs.append(cleaned_cert)

        return found_certs

    def _analyze_bullet_points(self, text: str) -> List[BulletPointAnalysis]:
        """
        Evaluates bullet points for strong action verbs and quantifiable metrics.
        """
        analyses = []
        metric_pattern = r"\b(?:\d+%(?:\.\d+)?|\$\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?(?:k|m|b)?\+?|\d+\s*(?:ms|seconds|minutes|hours|days|requests|users|records|tables))\b"

        for line in text.splitlines():
            cleaned = line.strip().lstrip("-*• ")
            if len(cleaned.split()) < 3:
                continue

            words = cleaned.split()
            first_word = re.sub(r"[^a-zA-Z]", "", words[0]).lower()
            starts_with_action = first_word in ACTION_VERBS

            # Check if any action verb exists
            has_action = any(re.sub(r"[^a-zA-Z]", "", w).lower() in ACTION_VERBS for w in words[:4])
            matched_action = first_word if starts_with_action else None

            # Detect metrics
            metrics = re.findall(metric_pattern, cleaned, re.IGNORECASE)

            analyses.append(BulletPointAnalysis(
                text=cleaned,
                has_action_verb=has_action or starts_with_action,
                starts_with_action_verb=starts_with_action,
                action_verb=matched_action,
                has_metric=len(metrics) > 0,
                metrics_found=metrics,
                word_count=len(words)
            ))

        return analyses
