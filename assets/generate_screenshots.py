"""
Generates high-resolution dashboard screenshot previews for AI Resume ATS Analyzer.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_preview_banner(filename: str, title: str, subtitle: str, highlights: list):
    width, height = 900, 500
    img = Image.new("RGB", (width, height), "#0F172A")
    draw = ImageDraw.Draw(img)

    # Top app bar
    draw.rectangle([0, 0, width, 55], fill="#1E293B")
    draw.ellipse([20, 20, 32, 32], fill="#EF4444")
    draw.ellipse([40, 20, 52, 52], fill="#F59E0B")
    draw.ellipse([60, 20, 72, 72], fill="#10B981")

    try:
        font_header = ImageFont.load_default(size=18)
        font_title = ImageFont.load_default(size=26)
        font_body = ImageFont.load_default(size=14)
        font_badge = ImageFont.load_default(size=13)
    except Exception:
        font_header = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    draw.text((100, 18), "AI Resume ATS Analyzer | Streamlit SaaS Dashboard", fill="#94A3B8", font=font_header)

    # Main Card
    card_box = [30, 80, width - 30, height - 30]
    draw.rounded_rectangle(card_box, radius=12, fill="#1E293B", outline="#334155", width=2)

    # Header inside card
    draw.text((60, 105), title, fill="#38BDF8", font=font_title)
    draw.text((60, 145), subtitle, fill="#94A3B8", font=font_body)

    # Metric blocks
    start_y = 190
    for idx, (label, val, col) in enumerate(highlights):
        x1 = 60 + (idx * 195)
        x2 = x1 + 180
        y1 = start_y
        y2 = start_y + 90
        draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill="#0F172A", outline=col, width=1)
        draw.text((x1 + 15, y1 + 15), val, fill=col, font=font_title)
        draw.text((x1 + 15, y1 + 55), label, fill="#94A3B8", font=font_badge)

    # Lower section visual
    draw.rounded_rectangle([60, 310, width - 60, 440], radius=8, fill="#0F172A", outline="#334155", width=1)
    draw.text((80, 330), "Core Engine Output & Interactive Visual Diagnostics", fill="#F8FAFC", font=font_header)
    draw.text((80, 365), "✓ Skills Match: 40% Weight | Direct & Fuzzy Token Boundary Matching", fill="#10B981", font=font_body)
    draw.text((80, 390), "✓ Keyword Match: 25% Weight | Scikit-learn TF-IDF Cosine Similarity Matrix", fill="#38BDF8", font=font_body)
    draw.text((80, 415), "✓ Dynamic Bullet Point Rewriting with Measurable Quantifiable Impact", fill="#F59E0B", font=font_body)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename, "PNG")
    print(f"Generated {filename}")

def main():
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    create_preview_banner(
        os.path.join(screenshots_dir, "dashboard_overview.png"),
        "ATS Score Dashboard & Executive Analytics",
        "Weighted multi-tier scoring (87/100) with Plotly gauge and category breakdown",
        [
            ("ATS Score", "87 / 100", "#10B981"),
            ("Skills Match", "85%", "#3B82F6"),
            ("Keyword Match", "78%", "#8B5CF6"),
            ("Experience Fit", "100%", "#10B981")
        ]
    )

    create_preview_banner(
        os.path.join(screenshots_dir, "skill_gap_analysis.png"),
        "Skill Gap & Domain Coverage Analysis",
        "Categorized matched skills (✓) vs missing skills (✗) with category radar & bar charts",
        [
            ("Matched Skills", "18 Found", "#10B981"),
            ("Missing Skills", "4 Gaps", "#EF4444"),
            ("Top Missing", "Docker, K8s", "#F59E0B"),
            ("Domain Coverage", "92% Fit", "#38BDF8")
        ]
    )

    create_preview_banner(
        os.path.join(screenshots_dir, "bullet_optimizer.png"),
        "AI Resume Improvement Suggestions",
        "Automated weak verb detection, metric insertion, and Before/After rewrite comparisons",
        [
            ("Weak Verbs Found", "3 Flagged", "#EF4444"),
            ("Rewrites Built", "5 Pairs", "#10B981"),
            ("Metric Density", "45% Missing", "#F59E0B"),
            ("STAR Method", "Active", "#8B5CF6")
        ]
    )

if __name__ == "__main__":
    main()
