"""
Visualizer module for AI Resume ATS Analyzer.
Generates interactive, production-ready Plotly charts for ATS scoring,
skill gaps, keyword frequency, and domain coverage.
"""

from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px
from analyzer.ats_score import ATSScoreReport
from analyzer.matcher import MatchResult


# Consistent modern SaaS color palette
THEME_COLORS = {
    "primary": "#3B82F6",      # Blue
    "success": "#10B981",      # Emerald Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Coral Red
    "accent": "#8B5CF6",       # Purple
    "teal": "#14B8A6",         # Teal
    "background": "rgba(0,0,0,0)",
    "text": "#E2E8F0",
    "grid": "rgba(255, 255, 255, 0.1)"
}


def create_ats_gauge_chart(score_report: ATSScoreReport) -> go.Figure:
    """
    Creates an ATS Score Gauge Chart with color segments,
    delta indicator, and threshold markers.
    """
    score = score_report.total_score

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>ATS Compatibility Score</b><br><span style='font-size:14px;color:#94A3B8'>{score_report.grade}</span>", 'font': {'size': 20, 'color': '#FFFFFF'}},
        delta={'reference': 75, 'increasing': {'color': '#10B981'}, 'decreasing': {'color': '#EF4444'}, 'position': "bottom"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8", 'tickfont': {'color': "#94A3B8"}},
            'bar': {'color': score_report.status_color, 'thickness': 0.28},
            'bgcolor': "rgba(255, 255, 255, 0.05)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.15)",
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.25)"},
                {'range': [50, 70], 'color': "rgba(245, 158, 11, 0.25)"},
                {'range': [70, 85], 'color': "rgba(59, 130, 246, 0.25)"},
                {'range': [85, 100], 'color': "rgba(16, 185, 129, 0.25)"}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 3},
                'thickness': 0.8,
                'value': 80
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font={'color': THEME_COLORS["text"], 'family': "Inter, system-ui, sans-serif"},
        height=320,
        margin=dict(l=25, r=25, t=55, b=25)
    )
    return fig


def create_skill_comparison_bar_chart(match: MatchResult) -> go.Figure:
    """
    Creates a grouped horizontal bar chart comparing Matched vs Missing skills
    across functional categories.
    """
    categories = []
    matched_counts = []
    missing_counts = []

    for cat, data in match.category_breakdown.items():
        # Shorten label for cleaner display
        display_name = cat.replace("Development", "").replace("Science & ", "").strip()
        categories.append(display_name)
        matched_counts.append(data["matched_count"])
        missing_counts.append(data["missing_count"])

    if not categories:
        categories = ["Overall Skills"]
        matched_counts = [len(match.matched_skills)]
        missing_counts = [len(match.missing_skills)]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=categories,
        x=matched_counts,
        name="Matched Skills",
        orientation='h',
        marker=dict(color="#10B981", line=dict(color="#059669", width=1.5)),
        text=matched_counts,
        textposition="auto"
    ))

    fig.add_trace(go.Bar(
        y=categories,
        x=missing_counts,
        name="Missing Skills",
        orientation='h',
        marker=dict(color="#EF4444", line=dict(color="#DC2626", width=1.5)),
        text=missing_counts,
        textposition="auto"
    ))

    fig.update_layout(
        barmode='stack',
        title="<b>Skill Breakdown by Category</b>",
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font={'color': THEME_COLORS["text"], 'family': "Inter, system-ui, sans-serif"},
        height=340,
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis=dict(title="Number of Skills", gridcolor=THEME_COLORS["grid"], zeroline=False),
        yaxis=dict(gridcolor=THEME_COLORS["grid"], autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_score_breakdown_chart(score_report: ATSScoreReport) -> go.Figure:
    """
    Creates a horizontal bar chart detailing points earned vs maximum points
    for each ATS component (Skills, Keywords, Experience, Projects).
    """
    components = []
    earned = []
    max_pts = []

    for name, item in score_report.weighted_breakdown.items():
        components.append(name)
        earned.append(item["contribution"])
        max_pts.append(item["max_points"])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=components,
        x=earned,
        name="Points Earned",
        orientation='h',
        marker=dict(
            color=["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B"],
            line=dict(color="rgba(255,255,255,0.2)", width=1)
        ),
        text=[f"{v:.1f} pts" for v in earned],
        textposition="inside",
        insidetextanchor="middle"
    ))

    fig.update_layout(
        title="<b>ATS Component Contribution (100 pts total)</b>",
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font={'color': THEME_COLORS["text"], 'family': "Inter, system-ui, sans-serif"},
        height=260,
        margin=dict(l=10, r=20, t=50, b=20),
        xaxis=dict(range=[0, 42], title="Points Contribution", gridcolor=THEME_COLORS["grid"]),
        yaxis=dict(autorange="reversed"),
        showlegend=False
    )
    return fig


def create_keyword_match_chart(top_keywords: List[Tuple[str, float]]) -> go.Figure:
    """
    Creates a bar chart displaying top matching keywords and their relevance score.
    """
    if not top_keywords:
        words = ["No Keywords"]
        scores = [0]
    else:
        words = [w[0].title() for w in top_keywords[:8]]
        scores = [w[1] for w in top_keywords[:8]]

    fig = go.Figure(go.Bar(
        x=words,
        y=scores,
        marker=dict(
            color=scores,
            colorscale=[[0, "#3B82F6"], [1, "#8B5CF6"]],
            line=dict(color="rgba(255,255,255,0.2)", width=1)
        ),
        text=[f"{s:.1f}%" for s in scores],
        textposition="outside"
    ))

    fig.update_layout(
        title="<b>Top Shared Semantic Keywords</b>",
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font={'color': THEME_COLORS["text"], 'family': "Inter, system-ui, sans-serif"},
        height=320,
        margin=dict(l=20, r=20, t=50, b=40),
        xaxis=dict(gridcolor=THEME_COLORS["grid"], tickangle=-25),
        yaxis=dict(title="Relevance Weight (%)", gridcolor=THEME_COLORS["grid"])
    )
    return fig


def create_radar_skill_chart(match: MatchResult) -> go.Figure:
    """
    Creates a Radar chart showing percentage coverage across skill domains.
    """
    categories = []
    percentages = []

    for cat, data in match.category_breakdown.items():
        short_cat = cat.replace("Development", "").replace("Science & ", "").strip()
        categories.append(short_cat)
        percentages.append(data["match_percentage"])

    if len(categories) < 3:
        # Pad with dummy categories if fewer than 3 to make radar display properly
        categories = ["Languages", "Frontend", "Backend", "Cloud/DevOps", "AI/ML", "Databases"]
        percentages = [match.skill_match_percentage] * 6

    # Close the radar loop
    radar_cats = categories + [categories[0]]
    radar_vals = percentages + [percentages[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=radar_vals,
        theta=radar_cats,
        fill='toself',
        fillcolor="rgba(59, 130, 246, 0.35)",
        line=dict(color="#3B82F6", width=2.5),
        name="Candidate Match %"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=THEME_COLORS["grid"]),
            angularaxis=dict(gridcolor=THEME_COLORS["grid"])
        ),
        paper_bgcolor=THEME_COLORS["background"],
        plot_bgcolor=THEME_COLORS["background"],
        font={'color': THEME_COLORS["text"], 'family': "Inter, system-ui, sans-serif"},
        height=340,
        margin=dict(l=35, r=35, t=50, b=35),
        title="<b>Skill Domain Coverage Radar</b>",
        showlegend=False
    )
    return fig
