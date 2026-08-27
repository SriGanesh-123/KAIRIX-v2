"""
Source Panel component for KAIRIX UI.

Renders syntax-highlighted legacy source code with metadata cards and line anchors in light mode.
"""
from __future__ import annotations

from typing import Any, Dict
import streamlit as st
from ui.components.metric_cards import format_metric


def render_source_metadata_card(file_info: Dict[str, Any]) -> None:
    """
    Renders top metadata bar for a selected source artifact in light theme without emojis.
    """
    tech = file_info.get("technology", "COBOL")
    tech_badge_cls = f"badge-{tech.lower()}"
    confidence = file_info.get("confidence", 90.0)

    total_lines_str = format_metric(file_info.get('total_lines', 0))
    entity_count_str = format_metric(file_info.get('entity_count', 0))
    rel_count_str = format_metric(file_info.get('relationship_count', 0))
    rule_count_str = format_metric(file_info.get('rule_count', 0))

    purpose_section = ""
    if file_info.get('purpose'):
        purpose_section = (
            '<div style="margin-top:0.75rem; padding:0.6rem 0.75rem; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; font-size:0.85rem; color:#334155;">'
            f'<b style="color:#0F172A;">Purpose:</b> {file_info.get("purpose")}'
            '</div>'
        )

    card_html = (
        '<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:1.25rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
        '<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
        '<div>'
        f'<span class="badge-tech {tech_badge_cls}">{tech}</span>'
        f'<h3 style="margin:0.4rem 0 0.2rem 0; color:#0F172A;">{file_info.get("file_name")}</h3>'
        f'<div style="font-size:0.8rem; color:#64748B; font-family:\'JetBrains Mono\', monospace;">'
        f'{file_info.get("relative_path", file_info.get("file_path"))}'
        '</div>'
        '</div>'
        '<div style="text-align:right;">'
        '<div style="font-size:0.75rem; color:#64748B; text-transform:uppercase; font-weight:600;">Confidence</div>'
        f'<div style="font-size:1.4rem; font-weight:700; color:#059669; font-family:\'JetBrains Mono\', monospace;">{confidence}%</div>'
        '</div>'
        '</div>'
        '<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:0.75rem; margin-top:1rem; padding-top:0.75rem; border-top:1px solid #F1F5F9;">'
        f'<div><div style="font-size:0.75rem; color:#64748B; font-weight:500;">Total Lines</div><div style="font-size:1.1rem; font-weight:700; color:#0F172A;">{total_lines_str}</div></div>'
        f'<div><div style="font-size:0.75rem; color:#64748B; font-weight:500;">Entities</div><div style="font-size:1.1rem; font-weight:700; color:#0284C7;">{entity_count_str}</div></div>'
        f'<div><div style="font-size:0.75rem; color:#64748B; font-weight:500;">Relationships</div><div style="font-size:1.1rem; font-weight:700; color:#059669;">{rel_count_str}</div></div>'
        f'<div><div style="font-size:0.75rem; color:#64748B; font-weight:500;">Business Rules</div><div style="font-size:1.1rem; font-weight:700; color:#D97706;">{rule_count_str}</div></div>'
        '</div>'
        f'{purpose_section}'
        '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)


def render_code_viewer(code: str, language: str = "cobol", height: int = 500) -> None:
    """
    Renders syntax-highlighted code with line numbers.
    """
    lang_map = {
        "COBOL": "cobol",
        "SQL": "sql",
        "SSIS": "xml",
    }
    st_lang = lang_map.get(language.upper(), "text")

    st.code(code, language=st_lang, line_numbers=True)
