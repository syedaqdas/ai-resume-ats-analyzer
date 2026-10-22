"""
Skill Extraction module for AI Resume ATS Analyzer.
Leverages regex pattern matching, spaCy NLP tokenization, and canonical taxonomies.
"""

import re
from collections import Counter
from typing import Dict, List, Set, Tuple

import spacy
from utils.skills_database import (
    SKILLS_TAXONOMY,
    SKILL_ALIASES,
    canonicalize_skill,
    get_all_skills,
    get_skill_category_map
)

# Load spaCy NLP model safely with fallback
_nlp = None


def get_nlp():
    """Lazily loads spaCy pipeline; falls back to blank model if needed."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = spacy.blank("en")
    return _nlp


class SkillExtractor:
    """
    Extracts and categorizes skills from technical text (resumes or job descriptions).
    """

    def __init__(self):
        self.all_skills = get_all_skills()
        self.category_map = get_skill_category_map()
        self._compiled_patterns = self._build_regex_patterns()

    def _build_regex_patterns(self) -> List[Tuple[str, re.Pattern, str]]:
        """
        Pre-compiles regex patterns for skills and aliases with appropriate word boundaries.
        Special care for C++, C#, .NET, CI/CD, React.js, Node.js, etc.
        """
        patterns = []

        # 1. Alias patterns
        for alias, canonical in SKILL_ALIASES.items():
            pattern = self._create_boundary_pattern(alias)
            patterns.append((alias, pattern, canonical))

        # 2. Canonical skill patterns
        for skill in self.all_skills:
            pattern = self._create_boundary_pattern(skill)
            patterns.append((skill.lower(), pattern, skill))

        # Sort patterns by length descending so multi-word phrases match before single words
        patterns.sort(key=lambda x: len(x[0]), reverse=True)
        return patterns

    def _create_boundary_pattern(self, term: str) -> re.Pattern:
        """
        Creates regex pattern with safe boundary matching for symbols like +, #, ., /
        """
        escaped = re.escape(term)
        # If term starts/ends with alphanumeric, enforce word boundary \b
        prefix = r"(?<![A-Za-z0-9])" if term[0].isalnum() else ""
        suffix = r"(?![A-Za-z0-9])" if term[-1].isalnum() else ""
        return re.compile(rf"{prefix}{escaped}{suffix}", re.IGNORECASE)

    def extract_skills(self, text: str) -> Tuple[List[str], Dict[str, List[str]], Dict[str, int]]:
        """
        Extracts skills from text.

        Returns:
            - List of unique canonical skills found
            - Dictionary of skills grouped by domain category
            - Frequency counts of each matched skill
        """
        if not text:
            return [], {cat: [] for cat in SKILLS_TAXONOMY}, {}

        text_lower = text.lower()
        matched_skills: Set[str] = set()
        skill_counts: Counter = Counter()

        for term, pattern, canonical in self._compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                canonical_name = canonicalize_skill(canonical)
                matched_skills.add(canonical_name)
                skill_counts[canonical_name] += len(matches)

        # Categorize matched skills
        categorized: Dict[str, List[str]] = {cat: [] for cat in SKILLS_TAXONOMY}
        for skill in matched_skills:
            cat = self.category_map.get(skill.lower(), "Tools & Methodologies")
            categorized[cat].append(skill)

        # Sort skills in each category alphabetically
        for cat in categorized:
            categorized[cat].sort()

        sorted_skills = sorted(list(matched_skills))
        return sorted_skills, categorized, dict(skill_counts)

    def extract_keywords_nlp(self, text: str, top_n: int = 15) -> List[str]:
        """
        Extracts top domain noun chunks and technical keywords using spaCy.
        """
        if not text:
            return []

        nlp = get_nlp()
        doc = nlp(text[:100000])  # Cap length for safety

        # Collect noun phrases and technical tokens
        candidates = []
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().lower()
            if len(chunk_text.split()) <= 3 and len(chunk_text) > 2:
                if not all(t.is_stop for t in chunk):
                    candidates.append(chunk_text)

        counts = Counter(candidates)
        # Exclude generic stopwords or numbers
        filtered = [
            term for term, _ in counts.most_common(top_n * 2)
            if not re.match(r"^\d+$", term)
        ]
        return filtered[:top_n]
