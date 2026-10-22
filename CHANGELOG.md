# Changelog

All notable changes to **AI Resume ATS Analyzer** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-23

### Added
- **Interactive Streamlit SaaS Dashboard:**
  - Modern glassmorphism UI with responsive card layouts and custom CSS badges.
  - Multi-tabbed executive results: Overview, Skill Gap, Bullet Optimizer, Structural Audit, and Report Export.
- **Multi-Engine PDF Extractor:**
  - Robust primary extraction using `pdfplumber` with automatic fallback to `pypdf`.
  - Comprehensive safety guards against password-encrypted, corrupt, empty, and scanned-image PDFs.
- **NLP Skill Extraction Engine:**
  - Multi-domain technical skills taxonomy (Programming, Frontend, Backend, Cloud & DevOps, Data/ML, Databases, Tools).
  - Regular expression boundaries with special-symbol support (`C++`, `C#`, `CI/CD`, `Go`, `SQL`).
  - Synonym and alias normalization (e.g., `k8s` -> `Kubernetes`, `reactjs` -> `React`).
  - spaCy `en_core_web_sm` pipeline integration for noun chunk and keyword analysis.
- **Intelligent ATS Scoring Engine:**
  - Exact four-tier weighted composite score formula:
    - Skills Match: 40%
    - Keyword Match (TF-IDF Cosine Similarity): 25%
    - Experience Match: 20%
    - Project Relevance: 15%
  - Color-coded status thresholds and grade classifications (Excellent, Good, Moderate, Needs Improvement).
- **Interactive Visualizations (Plotly Express & Graph Objects):**
  - ATS Score Gauge Chart with threshold indicators and delta marker.
  - Category comparison stacked bar chart (Matched vs Missing).
  - Skill domain radar chart.
  - Semantic keyword relevance bar chart.
- **AI Resume Improvement & Rewriting Generator:**
  - Passive/weak action verb scanner (flagging phrases like "worked on", "responsible for").
  - Automated dynamic bullet point rewrite generator providing concrete Before/After examples with quantifiable impact metrics.
  - STAR method project enhancement guidance.
  - Structural checklist audit for ATS standard readability.
- **Pre-Loaded Sample Datasets:**
  - 1-click evaluation presets for AI/ML Engineer and Full-Stack Python Developer roles.
- **Automated Pytest Test Suite:**
  - 21 unit tests spanning PDF extraction, regex parser, ATS scoring calculations, weight enforcement, and skill matching.
