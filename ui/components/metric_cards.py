"""
Metric Cards component for KAIRIX UI.

Renders high-impact KPI statistic cards with clean light borders, SVG icons, and accents.
Provides safe formatting helpers to prevent format specifier exceptions.
"""
from __future__ import annotations

from typing import Any, Optional
import streamlit as st
from ui.components.icons import get_icon


def format_metric(value: Any, default: str = "0") -> str:
    """
    Safely formats numeric and string metrics with comma thousands separators.
    Never throws formatting exceptions regardless of input type (int, float, str, None).
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.1f}"

    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        try:
            if "." in cleaned:
                val_float = float(cleaned)
                if val_float.is_integer():
                    return f"{int(val_float):,}"
                return f"{val_float:,.1f}"
            return f"{int(cleaned):,}"
        except (ValueError, TypeError):
            return str(value)

    return str(value)


def render_metric_card(
    label: str,
    value: Any,
    subtext: Optional[str] = None,
    icon_name: str = "dashboard",
    accent_color: str = "#0284C7",
) -> None:
    """
    Renders a single styled light-theme metric card with an SVG icon.
    """
    formatted_value = format_metric(value)
    icon_svg = get_icon(icon_name, size=15, color=accent_color)

    subtext_html = f'<div class="metric-subtext">{subtext}</div>' if subtext else ''
    card_html = (
        f'<div class="kairix-metric-card" style="border-top: 3px solid {accent_color};">'
        f'<div class="metric-label">'
        f'<span>{icon_svg}</span>'
        f'<span>{label}</span>'
        f'</div>'
        f'<div class="metric-value">{formatted_value}</div>'
        f'{subtext_html}'
        f'</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def render_primary_metrics(
    artifacts: Any,
    rules: Any,
    transformations: Optional[Any] = None,
    entities: Optional[Any] = None,
    relationships: Optional[Any] = None,
) -> None:
    """
    Renders the primary knowledge metrics across 2 columns in light mode with SVG icons.
    """
    col1, col2 = st.columns(2)

    with col1:
        render_metric_card(
            label="Source Artifacts",
            value=artifacts,
            subtext="COBOL, SQL & SSIS files",
            icon_name="folder",
            accent_color="#4F46E5",
        )

    with col2:
        tf_count = format_metric(transformations) if transformations is not None else "0"
        render_metric_card(
            label="Business Rules",
            value=rules,
            subtext=f"{tf_count} Transformations" if transformations else "Extracted business policies",
            icon_name="file-text",
            accent_color="#D97706",
        )
