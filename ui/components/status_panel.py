"""
Status Panel component for KAIRIX UI.

Renders backend connectivity diagnostics, latency metrics, and safe endpoint info
using structured, unindented HTML components in enterprise light mode without emojis.
"""
from __future__ import annotations

from typing import Any, Dict
import streamlit as st
from ui.components.metric_cards import format_metric
from ui.components.icons import get_icon


def render_service_health_card(
    title: str,
    status_dict: Dict[str, Any],
    icon_name: str = "server",
) -> None:
    """
    Renders an individual backend service health card in enterprise light theme.
    Guarantees proper HTML rendering without markdown code-block indentation bugs.
    """
    is_ok = bool(status_dict.get("connected") or status_dict.get("configured") or (status_dict.get("status") == "ready"))
    status_badge_class = "online" if is_ok else "offline"
    status_label = "ONLINE / CONNECTED" if is_ok else "OFFLINE / UNREACHABLE"
    dot_class = "dot-green" if is_ok else "dot-red"
    latency = status_dict.get("latency_ms", "—")

    nodes_count = format_metric(status_dict.get('total_nodes')) if 'total_nodes' in status_dict else None
    rels_count = format_metric(status_dict.get('total_relationships')) if 'total_relationships' in status_dict else None
    chunks_count = format_metric(status_dict.get('chunks_count')) if 'chunks_count' in status_dict else None
    summaries_count = format_metric(status_dict.get('summaries_count')) if 'summaries_count' in status_dict else None
    total_pts = format_metric(status_dict.get('total_points')) if 'total_points' in status_dict else None

    # Construct details lines
    detail_lines = []
    endpoint = status_dict.get('uri') or status_dict.get('url')
    if endpoint:
        detail_lines.append(f"<div><b>Endpoint:</b> <code style='color:#0284C7;'>{endpoint}</code></div>")
    if latency != "—":
        detail_lines.append(f"<div><b>Latency:</b> <code style='color:#059669;'>{latency} ms</code></div>")
    if nodes_count is not None:
        detail_lines.append(f"<div><b>Total Nodes:</b> <code>{nodes_count}</code></div>")
    if rels_count is not None:
        detail_lines.append(f"<div><b>Total Relationships:</b> <code>{rels_count}</code></div>")
    if chunks_count is not None:
        detail_lines.append(f"<div><b>Indexed Chunks:</b> <code>{chunks_count}</code></div>")
    if summaries_count is not None:
        detail_lines.append(f"<div><b>Indexed Summaries:</b> <code>{summaries_count}</code></div>")
    if total_pts is not None:
        detail_lines.append(f"<div><b>Total Vector Points:</b> <code>{total_pts}</code></div>")
    if 'provider' in status_dict:
        detail_lines.append(f"<div><b>Provider:</b> <code>{status_dict.get('provider')}</code></div>")
    if 'model' in status_dict:
        detail_lines.append(f"<div><b>Active Model:</b> <code>{status_dict.get('model')}</code></div>")
    if 'dimension' in status_dict:
        detail_lines.append(f"<div><b>Vector Dimension:</b> <code>{status_dict.get('dimension')}</code></div>")
    if 'masked_key' in status_dict:
        detail_lines.append(f"<div><b>API Key:</b> <code>{status_dict.get('masked_key')}</code></div>")

    details_html = "".join(detail_lines)
    icon_svg = get_icon(icon_name, size=18, color="#0284C7")
    message = status_dict.get('message', '')

    # Render without any multiline 4-space markdown indentations
    html_card = (
        '<div class="service-health-card">'
        '<div class="service-health-card-header">'
        f'<div class="service-health-title"><span>{icon_svg}</span> {title}</div>'
        f'<div class="service-health-badge {status_badge_class}">'
        f'<span class="status-dot {dot_class}"></span> {status_label}'
        '</div>'
        '</div>'
        f'<div class="service-health-details">{details_html}</div>'
        f'<div class="service-health-footer">{message}</div>'
        '</div>'
    )

    st.markdown(html_card, unsafe_allow_html=True)
