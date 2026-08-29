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
    total_lines_str = format_metric(file_info.get('total_lines', 0))
    entity_count_str = format_metric(file_info.get('entity_count', 0))
    rel_count_str = format_metric(file_info.get('relationship_count', 0))
    rule_count_str = format_metric(file_info.get('rule_count', 0))

    purpose_section = ""
    if file_info.get('purpose'):
        purpose_section = (
            '<div style="margin-top:0.95rem; padding:0.85rem 1.1rem; background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #2563EB; border-radius:10px; font-size:0.88rem; color:#1E40AF; line-height:1.5; box-shadow:inset 2px 2px 5px rgba(37, 99, 235, 0.12);">'
            f'<strong style="color:#0F172A;">Purpose:</strong> {file_info.get("purpose")}'
            '</div>'
        )

    card_html = (
        '<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-top:4px solid #2563EB; border-radius:16px; padding:1.35rem 1.6rem; margin-top:0.75rem; margin-bottom:1.35rem; box-shadow:8px 8px 20px rgba(166, 180, 200, 0.48), -8px -8px 20px rgba(255, 255, 255, 0.95);">'
        '<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
        '<div>'
        f'<span class="badge-tech {tech_badge_cls}">{tech}</span>'
        f'<h3 style="margin:0.5rem 0 0.25rem 0; color:#0F172A; font-size:1.38rem; font-weight:800; letter-spacing:-0.02em;">{file_info.get("file_name")}</h3>'
        '</div>'
        '</div>'

        '<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:0.85rem; margin-top:1.15rem;">'
        f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:10px; padding:0.65rem 0.85rem; box-shadow:3px 3px 8px rgba(166, 180, 200, 0.3), -3px -3px 8px rgba(255, 255, 255, 0.9);"><div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase;">Total Lines</div><div style="font-size:1.2rem; font-weight:800; color:#0F172A; font-family:\'JetBrains Mono\', monospace;">{total_lines_str}</div></div>'
        f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:10px; padding:0.65rem 0.85rem; box-shadow:3px 3px 8px rgba(166, 180, 200, 0.3), -3px -3px 8px rgba(255, 255, 255, 0.9);"><div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase;">Entities</div><div style="font-size:1.2rem; font-weight:800; color:#2563EB; font-family:\'JetBrains Mono\', monospace;">{entity_count_str}</div></div>'
        f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:10px; padding:0.65rem 0.85rem; box-shadow:3px 3px 8px rgba(166, 180, 200, 0.3), -3px -3px 8px rgba(255, 255, 255, 0.9);"><div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase;">Relationships</div><div style="font-size:1.2rem; font-weight:800; color:#059669; font-family:\'JetBrains Mono\', monospace;">{rel_count_str}</div></div>'
        f'<div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:10px; padding:0.65rem 0.85rem; box-shadow:3px 3px 8px rgba(166, 180, 200, 0.3), -3px -3px 8px rgba(255, 255, 255, 0.9);"><div style="font-size:0.72rem; color:#64748B; font-weight:700; text-transform:uppercase;">Business Rules</div><div style="font-size:1.2rem; font-weight:800; color:#D97706; font-family:\'JetBrains Mono\', monospace;">{rule_count_str}</div></div>'
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
