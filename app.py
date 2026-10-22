"""
AI Resume ATS Analyzer - Interactive Streamlit Application.
A SaaS-grade portfolio platform for evaluating resume ATS compatibility,
analyzing skill gaps, and generating targeted bullet-point rewrites.
"""

import io
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
import pandas as pd

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from analyzer.pdf_parser import extract_text_from_pdf, PDFParseResult
from analyzer.resume_parser import ResumeParser, ResumeData
from analyzer.matcher import JobDescriptionParser, ResumeMatcher, MatchResult, JobDescriptionData
from analyzer.ats_score import ATSScoreCalculator, ATSScoreReport
from analyzer.suggestions import SuggestionsGenerator, SuggestionsReport
from analyzer.visualizer import (
    create_ats_gauge_chart,
    create_skill_comparison_bar_chart,
    create_score_breakdown_chart,
    create_keyword_match_chart,
    create_radar_skill_chart
)
from utils.helpers import SAMPLE_RESUMES, SAMPLE_JOB_DESCRIPTIONS

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Resume ATS Analyzer | Smart Career Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS STYLING (Modern SaaS Design)
# ==========================================
CUSTOM_CSS = """
<style>
    /* Global Fonts & Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #94A3B8;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Skill Pill Badges */
    .skill-badge-matched {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    .skill-badge-missing {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    .skill-badge-extra {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.35);
        padding: 5px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }

    /* Before / After Rewrite Card */
    .rewrite-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 16px;
    }
    .rewrite-header {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .rewrite-before {
        background: rgba(239, 68, 68, 0.08);
        border-left: 4px solid #EF4444;
        padding: 10px 14px;
        border-radius: 4px;
        color: #FCA5A5;
        font-size: 0.92rem;
        margin-bottom: 10px;
    }
    .rewrite-after {
        background: rgba(16, 185, 129, 0.08);
        border-left: 4px solid #10B981;
        padding: 10px 14px;
        border-radius: 4px;
        color: #6EE7B7;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .rewrite-reason {
        font-size: 0.82rem;
        color: #94A3B8;
        font-style: italic;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# INITIALIZE STATE
# ==========================================
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "parsed_resume" not in st.session_state:
    st.session_state.parsed_resume = None
if "parsed_jd" not in st.session_state:
    st.session_state.parsed_jd = None
if "match_result" not in st.session_state:
    st.session_state.match_result = None
if "score_report" not in st.session_state:
    st.session_state.score_report = None
if "suggestions_report" not in st.session_state:
    st.session_state.suggestions_report = None


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_path = BASE_DIR / "assets" / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.title("🎯 AI Resume ATS")

    st.markdown("### 📌 Quick Presets")
    selected_sample = st.selectbox(
        "Load Sample Profile & Job Description",
        ["Select a preset...", "AI / ML Engineer", "Full-Stack Python Developer"],
        index=0
    )

    if selected_sample == "AI / ML Engineer":
        st.session_state.resume_text = SAMPLE_RESUMES["AI / ML Engineer"]
        st.session_state.jd_text = SAMPLE_JOB_DESCRIPTIONS["Senior Machine Learning Engineer"]
        st.success("Loaded AI/ML Engineer profile & JD!")
    elif selected_sample == "Full-Stack Python Developer":
        st.session_state.resume_text = SAMPLE_RESUMES["Full-Stack Python & React Developer"]
        st.session_state.jd_text = SAMPLE_JOB_DESCRIPTIONS["Full-Stack Python Engineer"]
        st.success("Loaded Full-Stack Developer profile & JD!")

    st.markdown("---")
    st.markdown("### ⚖️ ATS Scoring Formula")
    st.markdown("""
    - **Skills Match:** `40%`  
      *Direct & fuzzy matching against skills taxonomy*
    - **Keyword Resonance:** `25%`  
      *TF-IDF cosine similarity & phrase density*
    - **Experience Match:** `20%`  
      *Years of experience vs JD requirements*
    - **Project Relevance:** `15%`  
      *Demonstrated skills in project portfolios*
    """)

    st.markdown("---")
    st.markdown("### 🛠️ Architecture & Tech Stack")
    st.markdown("""
    - **NLP:** spaCy `en_core_web_sm`
    - **ML:** Scikit-Learn TF-IDF
    - **PDF Engine:** pdfplumber + pypdf
    - **Analytics:** Plotly Express
    - **UI:** Streamlit SaaS Layout
    """)

    st.markdown("---")
    st.markdown("👨‍💻 **Open-Source Software Project**")
    st.caption("AI-Resume-ATS-Analyzer v1.0.0 | MIT License")


# ==========================================
# HERO SECTION
# ==========================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">AI Resume ATS Analyzer</div>
    <div class="hero-sub">
        Transform your resume for modern Applicant Tracking Systems (ATS). 
        Analyze technical skill gaps, evaluate keyword resonance, simulate recruiter scoring algorithms, 
        and generate dynamic action-verb bullet rewrites.
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# UPLOAD & INPUT SECTION
# ==========================================
col_resume, col_jd = st.columns(2)

with col_resume:
    st.subheader("📄 1. Candidate Resume")
    resume_tab_pdf, resume_tab_text = st.tabs(["Upload PDF", "Paste Plain Text"])

    with resume_tab_pdf:
        uploaded_pdf = st.file_uploader(
            "Upload Resume (PDF format)",
            type=["pdf"],
            help="Upload your text-based resume in PDF format (up to 10MB)."
        )
        if uploaded_pdf is not None:
            with st.spinner("Extracting text from PDF..."):
                parse_res: PDFParseResult = extract_text_from_pdf(uploaded_pdf)
                if parse_res.is_valid:
                    st.session_state.resume_text = parse_res.text
                    st.success(f"✓ PDF extracted successfully ({parse_res.num_pages} page(s), {len(parse_res.text.split())} words)")
                else:
                    st.error(f"❌ {parse_res.error_message}")

    with resume_tab_text:
        pasted_resume = st.text_area(
            "Or Paste Resume Text directly:",
            value=st.session_state.resume_text,
            height=280,
            placeholder="Paste complete resume text here...",
            key="resume_text_area"
        )
        if pasted_resume != st.session_state.resume_text:
            st.session_state.resume_text = pasted_resume

with col_jd:
    st.subheader("💼 2. Job Description")
    jd_tab_text, jd_tab_upload = st.tabs(["Paste Text", "Upload File"])

    with jd_tab_text:
        pasted_jd = st.text_area(
            "Paste Job Description text:",
            value=st.session_state.jd_text,
            height=280,
            placeholder="Paste target job description and requirements here...",
            key="jd_text_area"
        )
        if pasted_jd != st.session_state.jd_text:
            st.session_state.jd_text = pasted_jd

    with jd_tab_upload:
        uploaded_jd = st.file_uploader(
            "Upload Job Description (PDF or TXT)",
            type=["pdf", "txt"],
            help="Upload the job posting as a PDF or text file."
        )
        if uploaded_jd is not None:
            if uploaded_jd.name.endswith(".pdf"):
                jd_pdf_res = extract_text_from_pdf(uploaded_jd)
                if jd_pdf_res.is_valid:
                    st.session_state.jd_text = jd_pdf_res.text
                    st.success(f"✓ Job description PDF parsed ({jd_pdf_res.num_pages} page(s))")
                else:
                    st.error(f"❌ {jd_pdf_res.error_message}")
            else:
                try:
                    st.session_state.jd_text = uploaded_jd.read().decode("utf-8")
                    st.success("✓ Job description text file loaded")
                except Exception as e:
                    st.error(f"Failed to read file: {e}")


# ==========================================
# TRIGGER ANALYSIS
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

with btn_col2:
    analyze_clicked = st.button(
        "🚀 Run Complete ATS Compatibility Analysis",
        use_container_width=True,
        type="primary"
    )

if analyze_clicked:
    if not st.session_state.resume_text.strip():
        st.warning("⚠️ Please provide a resume by uploading a PDF or pasting resume text.")
    elif not st.session_state.jd_text.strip():
        st.warning("⚠️ Please provide a job description to compare against.")
    else:
        with st.spinner("🤖 Processing with NLP pipeline & calculating ATS score..."):
            resume_parser = ResumeParser()
            jd_parser = JobDescriptionParser()
            matcher = ResumeMatcher()
            score_calc = ATSScoreCalculator()
            sugg_gen = SuggestionsGenerator()

            parsed_resume: ResumeData = resume_parser.parse(st.session_state.resume_text)
            parsed_jd: JobDescriptionData = jd_parser.parse(st.session_state.jd_text)
            match_result: MatchResult = matcher.match(parsed_resume, parsed_jd)
            score_report: ATSScoreReport = score_calc.calculate(match_result)
            sugg_report: SuggestionsReport = sugg_gen.generate(parsed_resume, match_result)

            st.session_state.parsed_resume = parsed_resume
            st.session_state.parsed_jd = parsed_jd
            st.session_state.match_result = match_result
            st.session_state.score_report = score_report
            st.session_state.suggestions_report = sugg_report
            st.session_state.analysis_done = True
            st.success("🎉 Analysis complete! Scroll down to explore your ATS evaluation.")


# ==========================================
# DASHBOARD RESULTS DISPLAY
# ==========================================
if st.session_state.analysis_done and st.session_state.score_report:
    score_report: ATSScoreReport = st.session_state.score_report
    match_result: MatchResult = st.session_state.match_result
    resume_data: ResumeData = st.session_state.parsed_resume
    jd_data: JobDescriptionData = st.session_state.parsed_jd
    suggestions: SuggestionsReport = st.session_state.suggestions_report

    st.markdown("---")
    st.header("📊 ATS Analysis Dashboard")

    # High-level Metrics Row
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {score_report.status_color};">{score_report.total_score}/100</div>
            <div class="metric-label">Composite ATS Score</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{score_report.skills_score:.0f}%</div>
            <div class="metric-label">Skills Match (40%)</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{score_report.keyword_score:.1f}%</div>
            <div class="metric-label">Keyword Match (25%)</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{score_report.experience_score:.0f}%</div>
            <div class="metric-label">Experience (20%)</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{score_report.project_score:.0f}%</div>
            <div class="metric-label">Project Match (15%)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for In-depth Breakdown
    tab_overview, tab_skills, tab_suggestions, tab_parsed_data, tab_export = st.tabs([
        "📈 Executive Visuals & Score",
        "🎯 Skill Gap Analysis",
        "💡 Bullet Optimizer & Suggestions",
        "📋 Profile & Structure Audit",
        "📄 Export Report"
    ])

    # ----------------------------------------------------
    # TAB 1: EXECUTIVE VISUALS & SCORE
    # ----------------------------------------------------
    with tab_overview:
        g_col1, g_col2 = st.columns([1, 1])

        with g_col1:
            gauge_fig = create_ats_gauge_chart(score_report)
            st.plotly_chart(gauge_fig, use_container_width=True)

        with g_col2:
            breakdown_fig = create_score_breakdown_chart(score_report)
            st.plotly_chart(breakdown_fig, use_container_width=True)

        st.markdown("#### 🔍 Performance Diagnostics")
        st.info(score_report.detailed_explanation)

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("##### ✅ Key Strengths")
            if score_report.strengths:
                for s in score_report.strengths:
                    st.markdown(f"- {s}")
            else:
                st.markdown("- Resume meets baseline formatting standards.")

        with d_col2:
            st.markdown("##### ⚠️ Improvement Opportunities")
            if score_report.weaknesses:
                for w in score_report.weaknesses:
                    st.markdown(f"- {w}")
            else:
                st.markdown("- No critical weak points identified!")

        st.markdown("<br>", unsafe_allow_html=True)
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            radar_fig = create_radar_skill_chart(match_result)
            st.plotly_chart(radar_fig, use_container_width=True)
        with r_col2:
            kw_fig = create_keyword_match_chart(match_result.top_matching_keywords)
            st.plotly_chart(kw_fig, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: SKILL GAP ANALYSIS
    # ----------------------------------------------------
    with tab_skills:
        st.subheader("🎯 Skill Gap Breakdown")

        sg_col1, sg_col2 = st.columns(2)
        with sg_col1:
            st.markdown(f"#### ✅ Matched Skills ({len(match_result.matched_skills)})")
            if match_result.matched_skills:
                badges = "".join([f'<span class="skill-badge-matched">✓ {s}</span>' for s in match_result.matched_skills])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.info("No direct skill matches found between resume and job description.")

        with sg_col2:
            st.markdown(f"#### ❌ Missing Skills ({len(match_result.missing_skills)})")
            if match_result.missing_skills:
                badges = "".join([f'<span class="skill-badge-missing">✗ {s}</span>' for s in match_result.missing_skills])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.success("Outstanding! You match all technical skills listed in the job description.")

        if match_result.extra_skills:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"#### 🌟 Additional Skills You Possess ({len(match_result.extra_skills)})")
            extra_badges = "".join([f'<span class="skill-badge-extra">+ {s}</span>' for s in match_result.extra_skills[:20]])
            st.markdown(extra_badges, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📊 Category Match Breakdown")
        comp_bar_fig = create_skill_comparison_bar_chart(match_result)
        st.plotly_chart(comp_bar_fig, use_container_width=True)

        # Table of category details
        cat_rows = []
        for cat, data in match_result.category_breakdown.items():
            cat_rows.append({
                "Domain Category": cat,
                "Required": data["total_required"],
                "Matched": data["matched_count"],
                "Missing": data["missing_count"],
                "Match %": f"{data['match_percentage']}%",
                "Missing Skills List": ", ".join(data["missing_skills"]) if data["missing_skills"] else "None (100% Match)"
            })
        if cat_rows:
            st.dataframe(pd.DataFrame(cat_rows), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # TAB 3: BULLET OPTIMIZER & SUGGESTIONS
    # ----------------------------------------------------
    with tab_suggestions:
        st.subheader("💡 Actionable Resume Rewrites & Recommendations")

        st.markdown("#### 🔄 Dynamic Bullet Point Rewrites (Before vs. After)")
        st.caption("Replacing passive phrasing and weak verbs with dynamic action verbs and measurable quantifiable impact.")

        if suggestions.bullet_rewrites:
            for i, rw in enumerate(suggestions.bullet_rewrites, 1):
                st.markdown(f"""
                <div class="rewrite-card">
                    <div class="rewrite-header">Recommendation #{i}</div>
                    <div class="rewrite-before"><b>Before:</b> "{rw.original}"</div>
                    <div class="rewrite-after"><b>After:</b> "{rw.suggested}"</div>
                    <div class="rewrite-reason">💡 <b>Rationale:</b> {rw.reason}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Your bullet points already display strong action verbs and metrics!")

        st.markdown("<br>", unsafe_allow_html=True)
        sugg_col1, sugg_col2 = st.columns(2)

        with sugg_col1:
            st.markdown("#### 📍 Strategic Keyword Insertion")
            for tip in suggestions.keyword_placement_tips:
                st.markdown(f"- {tip}")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🚀 Project Description Enhancements")
            for tip in suggestions.project_enhancement_tips:
                st.markdown(f"- {tip}")

        with sugg_col2:
            st.markdown("#### ⚠️ Weak Action Verbs Detected")
            if suggestions.weak_verbs_found:
                st.warning(f"Detected {len(suggestions.weak_verbs_found)} passive verbs: {', '.join(suggestions.weak_verbs_found)}")
                st.markdown("""
                **Replace with High-Impact Power Verbs:**
                - *Instead of 'Worked on'*: **Architected, Engineered, Spearheaded, Developed**
                - *Instead of 'Responsible for'*: **Orchestrated, Directed, Governed, Managed**
                - *Instead of 'Helped with'*: **Co-engineered, Accelerated, Delivered**
                - *Instead of 'Handled'*: **Administered, Streamlined, Optimized**
                """)
            else:
                st.success("Zero weak action verbs found. Excellent phrasing!")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📈 Quantifiable Impact Audit")
            st.info(
                f"**Metrics Coverage:** {suggestions.total_bullets_analyzed - suggestions.missing_metrics_count} / "
                f"{suggestions.total_bullets_analyzed} bullet points include quantifiable numbers or metrics. "
                "Aim for at least 70% metric density."
            )

    # ----------------------------------------------------
    # TAB 4: PROFILE & STRUCTURE AUDIT
    # ----------------------------------------------------
    with tab_parsed_data:
        st.subheader("📋 Parsed Candidate Information & Structural Audit")

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown("#### 👤 Candidate Contact Details")
            st.write(f"**Name:** {resume_data.name or 'Not clearly detected'}")
            st.write(f"**Email:** {resume_data.email or 'Missing'}")
            st.write(f"**Phone:** {resume_data.phone or 'Missing'}")
            st.write(f"**LinkedIn:** {resume_data.links.get('linkedin') or 'Not found'}")
            st.write(f"**GitHub:** {resume_data.links.get('github') or 'Not found'}")
            st.write(f"**Portfolio:** {resume_data.links.get('portfolio') or 'Not found'}")
            st.write(f"**Total Estimated Experience:** {resume_data.experience_years} years")

        with info_col2:
            st.markdown("#### 🎓 Education & Certifications")
            if resume_data.education:
                for edu in resume_data.education:
                    st.write(f"- **{edu['degree']}** ({edu['year']}) — {edu['raw_line']}")
            else:
                st.write("No explicit education records detected.")

            if resume_data.certifications:
                st.write("**Certifications:**")
                for c in resume_data.certifications:
                    st.write(f"- {c}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🏗️ ATS Structural Checklist Audit")
        audit_rows = []
        for audit in suggestions.structural_audits:
            audit_rows.append({
                "Section": audit.section_name,
                "Status": "✅ Present" if audit.is_present else "⚠️ Action Required",
                "Recommendation": audit.recommendation
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # TAB 5: EXPORT REPORT
    # ----------------------------------------------------
    with tab_export:
        st.subheader("📄 Export ATS Compatibility Report")

        # Generate markdown report text
        report_md = f"""# AI Resume ATS Compatibility Report
Generated by **AI Resume ATS Analyzer**
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary
- **Candidate Name:** {resume_data.name or 'Candidate'}
- **ATS Compatibility Score:** {score_report.total_score} / 100 ({score_report.grade})
- **Skills Match:** {score_report.skills_score}% (Weight: 40%)
- **Keyword Match:** {score_report.keyword_score}% (Weight: 25%)
- **Experience Match:** {score_report.experience_score}% (Weight: 20%)
- **Project Relevance:** {score_report.project_score}% (Weight: 15%)

---

## Skill Gap Analysis
### Matched Skills ({len(match_result.matched_skills)}):
{', '.join(match_result.matched_skills) if match_result.matched_skills else 'None'}

### Missing Skills ({len(match_result.missing_skills)}):
{', '.join(match_result.missing_skills) if match_result.missing_skills else 'None'}

---

## Actionable Improvement Suggestions
### Recommended Bullet Point Rewrites:
"""
        for i, rw in enumerate(suggestions.bullet_rewrites, 1):
            report_md += f"\n#### Rewrite #{i}:\n- **Before:** \"{rw.original}\"\n- **After:** \"{rw.suggested}\"\n- **Why:** {rw.reason}\n"

        report_md += f"""
---

## Structural & Formatting Audit
"""
        for audit in suggestions.structural_audits:
            report_md += f"- **{audit.section_name}**: {'PASSED' if audit.is_present else 'NEEDS ATTENTION'} — {audit.recommendation}\n"

        st.markdown(report_md)

        st.download_button(
            label="📥 Download Full ATS Report (Markdown)",
            data=report_md,
            file_name="ATS_Resume_Analysis_Report.md",
            mime="text/markdown",
            type="primary"
        )
