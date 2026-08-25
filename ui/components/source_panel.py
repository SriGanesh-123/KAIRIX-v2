"""
Source Panel component for KAIRIX UI.

Renders syntax-highlighted legacy source code with metadata cards and line anchors.
"""
from __future__ import annotations

import streamlit as st
from typing import Any, Dict, List, Optional


def render_source_metadata_card(file_info: Dict[str, Any]) -> None:
    """
    Renders top metadata bar for a selected source artifact.
    """
    tech = file_info.get("technology", "COBOL")
    tech_badge_cls = f"badge-{tech.lower()}"
    confidence = file_info.get("confidence", 90.0)

    st.markdown(
        f"""
        <div style="background:#161F30; border:1px solid #273549; border-radius:10px; padding:1.25rem; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <span class="badge-tech {tech_badge_cls}">{tech}</span>
                    <h3 style="margin:0.4rem 0 0.2rem 0; color:#FFFFFF;">{file_info.get('file_name')}</h3>
                    <div style="font-size:0.8rem; color:#64748B; font-family:'JetBrains Mono', monospace;">
                        {file_info.get('relative_path', file_info.get('file_path'))}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase;">Confidence</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#10B981; font-family:'JetBrains Mono', monospace;">
                        {confidence}%
                    </div>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:0.75rem; margin-top:1rem; padding-top:0.75rem; border-top:1px solid #1E293B;">
                <div>
                    <div style="font-size:0.75rem; color:#64748B;">Total Lines</div>
                    <div style="font-size:1.1rem; font-weight:600; color:#F3F4F6;">{file_info.get('total_lines', 0):,}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#64748B;">Entities</div>
                    <div style="font-size:1.1rem; font-weight:600; color:#38BDF8;">{file_info.get('entity_count', 0)}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#64748B;">Relationships</div>
                    <div style="font-size:1.1rem; font-weight:600; color:#34D399;">{file_info.get('relationship_count', 0)}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#64748B;">Business Rules</div>
                    <div style="font-size:1.1rem; font-weight:600; color:#FBBF24;">{file_info.get('rule_count', 0)}</div>
                </div>
            </div>

            {f'''
            <div style="margin-top:0.75rem; padding:0.6rem 0.75rem; background:#0B0F19; border-radius:6px; font-size:0.85rem; color:#CBD5E1;">
                <b>Purpose:</b> {file_info.get('purpose')}
            </div>
            ''' if file_info.get('purpose') else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_code_viewer(code: str, language: str = "cobol", height: int = 500) -> None:
    """
    Renders syntax-highlighted code with line numbers in a monospaced block.
    """
    lang_map = {
        "COBOL": "cobol",
        "SQL": "sql",
        "SSIS": "xml",
    }
    st_lang = lang_map.get(language.upper(), "text")

    st.code(code, language=st_lang, line_numbers=True)
