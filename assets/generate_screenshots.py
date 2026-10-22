"""
Generates high-resolution dashboard screenshot previews for AI Resume ATS Analyzer
strictly matching the required filenames:
- dashboard.png
- ats_score.png
- skill_gap.png
- suggestions.png
"""
from PIL import Image, ImageDraw, ImageFont
import os

def get_fonts():
    try:
        font_header = ImageFont.load_default(size=18)
        font_large = ImageFont.load_default(size=32)
        font_title = ImageFont.load_default(size=24)
        font_body = ImageFont.load_default(size=15)
        font_small = ImageFont.load_default(size=13)
        font_badge = ImageFont.load_default(size=12)
    except Exception:
        font_header = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_badge = ImageFont.load_default()
    return font_header, font_large, font_title, font_body, font_small, font_badge

def draw_window_frame(draw, width, height, title_text):
    font_header, _, _, _, _, _ = get_fonts()
    # App Header Bar
    draw.rectangle([0, 0, width, 55], fill="#1E293B")
    # Window action buttons
    draw.ellipse([20, 20, 32, 32], fill="#EF4444")
    draw.ellipse([40, 20, 52, 52], fill="#F59E0B")
    draw.ellipse([60, 20, 72, 72], fill="#10B981")
    draw.text((100, 18), title_text, fill="#94A3B8", font=font_header)

def create_dashboard_screenshot(filepath: str):
    width, height = 1100, 680
    img = Image.new("RGB", (width, height), "#0B1120")
    draw = ImageDraw.Draw(img)
    _, font_large, font_title, font_body, font_small, font_badge = get_fonts()
    draw_window_frame(draw, width, height, "AI Resume ATS Analyzer | Modern SaaS Application")

    # Hero Banner inside
    draw.rounded_rectangle([30, 75, width - 30, 160], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 92), "AI Resume ATS Analyzer", fill="#38BDF8", font=font_title)
    draw.text((55, 126), "Evaluate resume compatibility, uncover skill gaps, and simulate ATS screening algorithms.", fill="#94A3B8", font=font_small)

    # 4 Metric Cards
    metrics = [
        ("Composite ATS Score", "87 / 100", "#10B981", "Excellent Match"),
        ("Skills Match (40%)", "85.0%", "#3B82F6", "18/22 Skills"),
        ("Keyword Match (25%)", "78.4%", "#8B5CF6", "TF-IDF Resonance"),
        ("Experience Match (20%)", "100%", "#10B981", "5.5 yrs / 4 yrs"),
    ]
    card_w = (width - 60 - 45) // 4
    for i, (label, val, col, sub) in enumerate(metrics):
        cx1 = 30 + i * (card_w + 15)
        cx2 = cx1 + card_w
        draw.rounded_rectangle([cx1, 180, cx2, 275], radius=10, fill="#1E293B", outline=col, width=1)
        draw.text((cx1 + 18, 195), val, fill=col, font=font_large)
        draw.text((cx1 + 18, 235), label, fill="#E2E8F0", font=font_small)
        draw.text((cx1 + 18, 253), sub, fill="#94A3B8", font=font_badge)

    # Main Dashboard Sections
    # Left: Plotly ATS Gauge representation
    draw.rounded_rectangle([30, 295, 530, 645], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 315), "ATS Compatibility Score Gauge", fill="#F8FAFC", font=font_title)
    # Arc / gauge visual
    draw.arc([130, 360, 430, 620], start=180, end=0, fill="#334155", width=28)
    draw.arc([130, 360, 430, 620], start=180, end=-25, fill="#10B981", width=28)
    draw.text((230, 460), "87%", fill="#10B981", font=font_large)
    draw.text((205, 505), "Strong ATS Candidate", fill="#94A3B8", font=font_small)
    draw.text((150, 560), "Threshold: 75% | Target: 85%+", fill="#64748B", font=font_badge)

    # Right: Domain Breakdown & Diagnostics
    draw.rounded_rectangle([550, 295, width - 30, 645], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((575, 315), "Performance Diagnostics & Coverage", fill="#F8FAFC", font=font_title)

    bars = [
        ("Programming Languages", 95, "#3B82F6"),
        ("Cloud & DevOps", 75, "#10B981"),
        ("Data Science & ML", 90, "#8B5CF6"),
        ("Backend Frameworks", 80, "#F59E0B"),
        ("Databases & Storage", 85, "#14B8A6")
    ]
    by = 365
    for cat, pct, col in bars:
        draw.text((575, by), cat, fill="#E2E8F0", font=font_small)
        draw.text((980, by), f"{pct}%", fill=col, font=font_small)
        # Background bar
        draw.rounded_rectangle([575, by + 22, 1030, by + 34], radius=6, fill="#0F172A")
        # Fill bar
        bar_len = int(575 + (1030 - 575) * (pct / 100))
        draw.rounded_rectangle([575, by + 22, bar_len, by + 34], radius=6, fill=col)
        by += 52

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, "PNG")
    print(f"Generated {filepath}")

def create_ats_score_screenshot(filepath: str):
    width, height = 1100, 680
    img = Image.new("RGB", (width, height), "#0B1120")
    draw = ImageDraw.Draw(img)
    _, font_large, font_title, font_body, font_small, font_badge = get_fonts()
    draw_window_frame(draw, width, height, "AI Resume ATS Analyzer | ATS Score Deep Dive")

    # Header Card
    draw.rounded_rectangle([30, 75, width - 30, 160], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 92), "Executive ATS Score Breakdown (87 / 100)", fill="#10B981", font=font_title)
    draw.text((55, 126), "Strict weighted formula: Skills 40% + Keywords 25% + Experience 20% + Projects 15%", fill="#94A3B8", font=font_small)

    # 4 Weighted Pillars
    pillars = [
        ("Skills Match (40% Weight)", "34.0 / 40 pts", "85.0% Direct & Fuzzy Coverage", "#3B82F6"),
        ("Keyword Match (25% Weight)", "19.6 / 25 pts", "78.4% TF-IDF Cosine Similarity", "#8B5CF6"),
        ("Experience (20% Weight)", "20.0 / 20 pts", "5.5 yrs candidate vs 4 yrs JD", "#10B981"),
        ("Project Relevance (15% Weight)", "13.2 / 15 pts", "88% Demonstrated Technology Fit", "#F59E0B"),
    ]
    py = 180
    for title, score, desc, col in pillars:
        draw.rounded_rectangle([30, py, width - 30, py + 95], radius=10, fill="#1E293B", outline=col, width=1)
        draw.text((55, py + 18), title, fill="#F8FAFC", font=font_title)
        draw.text((55, py + 55), desc, fill="#94A3B8", font=font_small)
        draw.text((width - 250, py + 25), score, fill=col, font=font_large)
        py += 115

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, "PNG")
    print(f"Generated {filepath}")

def create_skill_gap_screenshot(filepath: str):
    width, height = 1100, 680
    img = Image.new("RGB", (width, height), "#0B1120")
    draw = ImageDraw.Draw(img)
    _, _, font_title, font_body, font_small, font_badge = get_fonts()
    draw_window_frame(draw, width, height, "AI Resume ATS Analyzer | Skill Gap & Domain Taxonomy")

    # Header Card
    draw.rounded_rectangle([30, 75, width - 30, 150], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 92), "Skill Gap Analysis (Matched vs. Missing)", fill="#38BDF8", font=font_title)
    draw.text((55, 122), "Cross-referenced against 200+ canonical technical skills with alias normalization.", fill="#94A3B8", font=font_small)

    # Left: Matched Skills
    draw.rounded_rectangle([30, 170, 530, 645], radius=12, fill="#1E293B", outline="#10B981", width=1)
    draw.text((55, 190), "Matched Skills (18 Identified)", fill="#10B981", font=font_title)

    matched_skills = [
        "✓ Python", "✓ PyTorch", "✓ TensorFlow", "✓ Scikit-learn",
        "✓ Pandas", "✓ NumPy", "✓ NLP", "✓ Docker",
        "✓ Kubernetes", "✓ AWS", "✓ SQL", "✓ PostgreSQL",
        "✓ Git", "✓ CI/CD", "✓ Redis", "✓ FastApi", "✓ Linux", "✓ Bash"
    ]
    sx, sy = 55, 235
    for s in matched_skills:
        draw.rounded_rectangle([sx, sy, sx + 135, sy + 36], radius=18, fill="#064E3B", outline="#10B981")
        draw.text((sx + 15, sy + 8), s, fill="#10B981", font=font_small)
        sx += 150
        if sx > 450:
            sx = 55
            sy += 48

    # Right: Missing Skills
    draw.rounded_rectangle([550, 170, width - 30, 645], radius=12, fill="#1E293B", outline="#EF4444", width=1)
    draw.text((575, 190), "Missing Skills (4 Gaps)", fill="#EF4444", font=font_title)

    missing_skills = [
        ("✗ Terraform", "Critical", "#EF4444"),
        ("✗ MLflow", "Important", "#F59E0B"),
        ("✗ LangChain", "Recommended", "#3B82F6"),
        ("✗ BigQuery", "Nice-to-have", "#94A3B8")
    ]
    msy = 240
    for name, priority, col in missing_skills:
        draw.rounded_rectangle([575, msy, width - 60, msy + 70], radius=8, fill="#0F172A", outline=col)
        draw.text((595, msy + 15), name, fill="#F8FAFC", font=font_title)
        draw.text((595, msy + 44), f"Priority Level: {priority}", fill=col, font=font_badge)
        draw.text((880, msy + 25), "Add to Skills", fill="#38BDF8", font=font_small)
        msy += 85

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, "PNG")
    print(f"Generated {filepath}")

def create_suggestions_screenshot(filepath: str):
    width, height = 1100, 680
    img = Image.new("RGB", (width, height), "#0B1120")
    draw = ImageDraw.Draw(img)
    _, _, font_title, font_body, font_small, font_badge = get_fonts()
    draw_window_frame(draw, width, height, "AI Resume ATS Analyzer | Resume Improvement Rewriter")

    # Header Card
    draw.rounded_rectangle([30, 75, width - 30, 150], radius=12, fill="#1E293B", outline="#334155", width=1)
    draw.text((55, 92), "AI Resume Improvement Suggestions", fill="#C084FC", font=font_title)
    draw.text((55, 122), "Automated weak action verb replacement and quantifiable impact metric insertion.", fill="#94A3B8", font=font_small)

    # Rewrite Cards
    rewrites = [
        (
            "Recommendation #1 (Weak Phrasing Detected: 'worked on')",
            "Worked on web application with Python and React.",
            "Engineered a responsive React web application, improving user retention by 28% and reducing load times by 40%.",
            "Swapped passive verb 'worked on' for strong verb 'Engineered' and added quantifiable impact metrics."
        ),
        (
            "Recommendation #2 (Missing Measurable Metrics)",
            "Responsible for database backups and server monitoring.",
            "Orchestrated automated PostgreSQL backup pipelines across AWS, achieving 99.99% service uptime.",
            "Replaced 'Responsible for' with power verb 'Orchestrated' and incorporated high-availability metric."
        )
    ]
    ry = 170
    for title, before, after, reason in rewrites:
        draw.rounded_rectangle([30, ry, width - 30, ry + 215], radius=12, fill="#1E293B", outline="#334155")
        draw.text((55, ry + 16), title, fill="#38BDF8", font=font_body)
        # Before block
        draw.rounded_rectangle([55, ry + 42, width - 60, ry + 88], radius=6, fill="#3B1C1C", outline="#EF4444")
        draw.text((70, ry + 55), f"Before:  \"{before}\"", fill="#FCA5A5", font=font_small)
        # After block
        draw.rounded_rectangle([55, ry + 100, width - 60, ry + 150], radius=6, fill="#064E3B", outline="#10B981")
        draw.text((70, ry + 115), f"After:   \"{after}\"", fill="#6EE7B7", font=font_body)
        # Rationale
        draw.text((55, ry + 168), f"💡 Rationale: {reason}", fill="#94A3B8", font=font_badge)
        ry += 235

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath, "PNG")
    print(f"Generated {filepath}")

def main():
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    create_dashboard_screenshot(os.path.join(screenshots_dir, "dashboard.png"))
    create_ats_score_screenshot(os.path.join(screenshots_dir, "ats_score.png"))
    create_skill_gap_screenshot(os.path.join(screenshots_dir, "skill_gap.png"))
    create_suggestions_screenshot(os.path.join(screenshots_dir, "suggestions.png"))

if __name__ == "__main__":
    main()
