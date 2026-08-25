"""
Status Panel component for KAIRIX UI.

Renders backend connectivity diagnostics, latency metrics, and safe endpoint info.
"""
from __future__ import annotations

import streamlit as st
from typing import Any, Dict


def render_service_health_card(
    title: str,
    status_dict: Dict[str, Any],
    icon: str = "🔌",
) -> None:
    """
    Renders an individual backend service health card.
    """
    is_ok = status_dict.get("connected") or status_dict.get("configured") or (status_dict.get("status") == "ready")
    status_color = "#10B981" if is_ok else "#EF4444"
    status_label = "ONLINE / CONNECTED" if is_ok else "OFFLINE / UNREACHABLE"
    latency = status_dict.get("latency_ms", "—")

    st.markdown(
        f"""
        <div style="background:#161F30; border:1px solid #273549; border-top:3px solid {status_color}; border-radius:10px; padding:1.25rem; margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <div style="font-size:1.1rem; font-weight:600; color:#FFFFFF; display:flex; align-items:center; gap:0.5rem;">
                    <span>{icon}</span> {title}
                </div>
                <div style="display:flex; align-items:center; gap:0.4rem; font-size:0.75rem; font-weight:700; color:{status_color};">
                    <span class="status-dot {'dot-green' if is_ok else 'dot-red'}"></span>
                    {status_label}
                </div>
            </div>
            
            <div style="font-size:0.85rem; color:#94A3B8; line-height:1.6;">
                {f"<div><b>Endpoint:</b> <code style='color:#38BDF8;'>{status_dict.get('uri') or status_dict.get('url')}</code></div>" if status_dict.get('uri') or status_dict.get('url') else ""}
                {f"<div><b>Latency:</b> <code style='color:#34D399;'>{latency} ms</code></div>" if latency != '—' else ""}
                {f"<div><b>Total Nodes:</b> <code>{status_dict.get('total_nodes', 0):,}</code></div>" if 'total_nodes' in status_dict else ""}
                {f"<div><b>Total Relationships:</b> <code>{status_dict.get('total_relationships', 0):,}</code></div>" if 'total_relationships' in status_dict else ""}
                {f"<div><b>Indexed Chunks:</b> <code>{status_dict.get('chunks_count', 0):,}</code></div>" if 'chunks_count' in status_dict else ""}
                {f"<div><b>Indexed Summaries:</b> <code>{status_dict.get('summaries_count', 0):,}</code></div>" if 'summaries_count' in status_dict else ""}
                {f"<div><b>Provider:</b> <code>{status_dict.get('provider')}</code></div>" if 'provider' in status_dict else ""}
                {f"<div><b>Active Model:</b> <code>{status_dict.get('model')}</code></div>" if 'model' in status_dict else ""}
                {f"<div><b>Dimension:</b> <code>{status_dict.get('dimension')}</code></div>" if 'dimension' in status_dict else ""}
            </div>
            
            <div style="margin-top:0.75rem; font-size:0.8rem; color:#64748B;">
                {status_dict.get('message', '')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
