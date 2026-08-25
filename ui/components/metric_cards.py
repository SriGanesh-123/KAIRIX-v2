"""
Metric Cards component for KAIRIX UI.

Renders high-impact KPI statistic cards with glowing borders and icons.
"""
from __future__ import annotations

import streamlit as st
from typing import Optional


def render_metric_card(
    label: str,
    value: str | int | float,
    subtext: Optional[str] = None,
    icon: str = "📊",
    accent_color: str = "#38BDF8",
) -> None:
    """
    Renders a single styled metric card.
    """
    st.markdown(
        f"""
        <div class="kairix-metric-card" style="border-top: 3px solid {accent_color};">
            <div class="metric-label">
                <span>{icon}</span>
                <span>{label}</span>
            </div>
            <div class="metric-value">{value:, if isinstance(value, (int, float)) else value}</div>
            {f'<div class="metric-subtext">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_primary_metrics(
    artifacts: int,
    entities: int,
    relationships: int,
    rules: int,
    transformations: Optional[int] = None,
) -> None:
    """
    Renders the 4 primary knowledge graph metrics across 4 columns.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            label="Source Artifacts",
            value=artifacts,
            subtext="COBOL, SQL & SSIS files",
            icon="📁",
            accent_color="#818CF8",
        )

    with col2:
        render_metric_card(
            label="Extracted Entities",
            value=entities,
            subtext="Tables, Columns, Variables",
            icon="🧩",
            accent_color="#38BDF8",
        )

    with col3:
        render_metric_card(
            label="Graph Relationships",
            value=relationships,
            subtext="Data flows & dependencies",
            icon="🕸️",
            accent_color="#34D399",
        )

    with col4:
        render_metric_card(
            label="Business Rules",
            value=rules,
            subtext=f"{transformations or 0} Transformations" if transformations else "Extracted business policies",
            icon="📜",
            accent_color="#FBBF24",
        )
