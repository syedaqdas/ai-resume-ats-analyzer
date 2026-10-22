"""
Generates a modern SaaS logo for AI Resume ATS Analyzer.
"""
from PIL import Image, ImageDraw, ImageFont
import os

def generate_logo():
    width, height = 400, 100
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw rounded icon background (gradient-like purple/blue)
    icon_box = [10, 10, 90, 90]
    draw.rounded_rectangle(icon_box, radius=18, fill="#3B82F6", outline="#60A5FA", width=2)

    # Draw checkmark / document graphic inside icon
    # Document outline
    doc_box = [30, 22, 70, 78]
    draw.rounded_rectangle(doc_box, radius=6, fill="#1E293B", outline="#93C5FD", width=2)
    # Checkmark inside doc
    check_coords = [(40, 52), (48, 62), (62, 38)]
    draw.line(check_coords, fill="#10B981", width=4, joint="curve")

    # Draw text: "RESUME" (White) "ATS" (Green/Blue) "AI"
    try:
        # Default font
        font_large = ImageFont.load_default(size=28)
        font_sub = ImageFont.load_default(size=12)
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((108, 22), "RESUME", fill="#F8FAFC", font=font_large)
    draw.text((230, 22), "ATS", fill="#38BDF8", font=font_large)
    draw.text((110, 58), "AI-POWERED MATCHER & AUDITOR", fill="#94A3B8", font=font_sub)

    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    image.save(out_path, "PNG")
    print(f"Saved logo to {out_path}")

if __name__ == "__main__":
    generate_logo()
