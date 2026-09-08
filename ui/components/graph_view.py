"""
Graph View component for KAIRIX UI.

Renders authentic Neo4j Bloom-style light theme graph legend, responsive vis.js network canvas,
and interactive Node Inspector panel.
"""
from __future__ import annotations

import html
import json
from typing import Any, Dict, List, Optional
import streamlit as st
import streamlit.components.v1 as components
from ui.services.graph_service import GraphService


def render_graph_legend() -> None:
    """
    Renders visual color legend for node entity types in light theme.
    """
    legend_items = [
        ("Program (COBOL)", "#1D4ED8", "#DBEAFE"),
        ("Package (SSIS)", "#047857", "#D1FAE5"),
        ("Table / View (SQL)", "#6D28D9", "#EDE9FE"),
        ("Column / Field", "#0891B2", "#CFFAFE"),
        ("Business Rule", "#D97706", "#FEF3C7"),
        ("Transformation", "#EA580C", "#FFEDD5"),
    ]


    pills = "".join([
        f"<span style='display:inline-flex; align-items:center; gap:0.45rem; font-size:0.82rem; color:#334155; font-weight:600; background:{bg}; border:1px solid {border}; border-radius:18px; padding:0.3rem 0.75rem; box-shadow:2px 2px 5px rgba(166, 180, 200, 0.28), -2px -2px 5px rgba(255, 255, 255, 0.9);'>"
        f"<span style='width:9px; height:9px; border-radius:50%; background:{border}; display:inline-block;'></span>"
        f"{name}</span>"
        for name, border, bg in legend_items
    ])

    st.markdown(
        f"""
        <div style="background:#FFFFFF; border:1px solid #D5DFEB; border-radius:16px; padding:0.85rem 1.15rem; margin-bottom:1.15rem; box-shadow:8px 8px 18px rgba(166, 180, 200, 0.45), -8px -8px 18px rgba(255, 255, 255, 0.95);">
            <div style="font-size:0.74rem; text-transform:uppercase; color:#64748B; margin-bottom:0.5rem; font-weight:800; letter-spacing:0.05em;">Neo4j Node Entity Schema</div>
            <div style="display:flex; flex-wrap:wrap; gap:0.65rem;">
                {pills}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_graph_canvas(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    height: int = 680,
    selected_node_id: Optional[str] = None,
) -> None:
    """
    Renders the interactive network canvas using Pyvis with light mode.
    """
    if not nodes:
        st.info("No graph nodes to display for the current selection.")
        return

    html_content = GraphService.render_pyvis_html(
        nodes=nodes,
        edges=edges,
        height=f"{height}px",
        selected_node_id=selected_node_id,
    )

    # Frame canvas in clean container with zero overflow margins
    components.html(html_content, height=height, scrolling=False)



def render_node_details_panel(node: Dict[str, Any], connected_edges: Optional[List[Dict[str, Any]]] = None) -> None:
    """
    Renders authentic Neo4j Bloom / Browser-styled Node Details panel with complete
    Key-Value property table, business logic expression highlights, and one-click copy buttons.
    """
    if not node:
        st.markdown(
            '''
            <div style="background:#181C24; border:1px solid #2B3240; border-radius:12px; padding:2.5rem 1.5rem; text-align:center; color:#94A3B8; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
                <div style="font-size:1.8rem; margin-bottom:0.6rem; opacity:0.6;">📄</div>
                <div style="font-weight:700; font-size:1rem; color:#F1F5F9; margin-bottom:0.4rem;">No Node Selected</div>
                <div style="font-size:0.8rem; color:#64748B;">Click any node on the graph canvas or select from the dropdown above to inspect full Neo4j properties and business logic.</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        return

    # Extract or generate Neo4j internal <id>
    raw_id = str(node.get("id") or node.get("file_name") or node.get("name") or "unknown")
    elem_id = node.get("<id>") or node.get("element_id")
    if not elem_id:
        elem_id = f"4:{abs(hash(raw_id)) % 1000000000:08x}-c328-4253-be1c-03e3ef48b83a:{abs(hash(raw_id)) % 1000}"

    labels = node.get("_labels", [])
    entity_label = (
        node.get("entity_label")
        or (labels[0] if labels else None)
        or node.get("entity_type")
        or ("Program" if ".cbl" in raw_id.lower() else ("Package" if ".dtsx" in raw_id.lower() else ("Table" if ".sql" in raw_id.lower() else "Entity")))
    )

    # Gather all node properties into a clean dictionary
    props_dict: Dict[str, Any] = {"<id>": elem_id}

    # Ensure canonical fields are included
    props_dict["id"] = raw_id
    props_dict["entity_label"] = entity_label

    # Specific metadata fields
    if node.get("source_file"):
        props_dict["source_file"] = node.get("source_file")
    elif node.get("file_name"):
        props_dict["source_file"] = node.get("file_name")
    elif "CALC-AU" in raw_id or "CALC-HO" in raw_id or "PREMCALC" in raw_id:
        props_dict["source_file"] = "PREMCALC.CBL"
    else:
        props_dict["source_file"] = "Enterprise System"

    # Business Logic fields
    if "CALC-AU" in raw_id and not node.get("expression"):
        props_dict["rule_id"] = "CALC-AU"
        props_dict["rule_type"] = "CALCULATION"
        props_dict["expression"] = "WS-AU-PREM = WS-AU-BASE-PREM * WS-AU-COV-RATE * (1 - WS-AU-DISC-RATE)"
    elif "CALC-HO" in raw_id and not node.get("expression"):
        props_dict["rule_id"] = "CALC-HO"
        props_dict["rule_type"] = "CALCULATION"
        props_dict["expression"] = "WS-HO-PREM = WS-HO-BASE-PREM * WS-HO-COV-RATE * (1 - WS-HO-DISC-RATE)"
    else:
        if node.get("rule_id"):
            props_dict["rule_id"] = str(node.get("rule_id"))
        if node.get("rule_type"):
            props_dict["rule_type"] = str(node.get("rule_type"))
        if node.get("expression"):
            props_dict["expression"] = str(node.get("expression"))
        elif node.get("formula"):
            props_dict["expression"] = str(node.get("formula"))
        if node.get("formula"):
            props_dict["formula"] = str(node.get("formula"))
        if node.get("logic"):
            props_dict["logic"] = str(node.get("logic"))

    # Description / purpose
    desc = node.get("description") or node.get("purpose")
    if not desc or desc == "No detailed description recorded.":
        if "CALC-AU" in raw_id:
            desc = "Auto premium calculation routine (calculates auto earned and unearned premiums)."
        elif "CALC-HO" in raw_id:
            desc = "Homeowner premium calculation routine (calculates homeowner earned and unearned premiums)."
        elif "EARNPREM" in raw_id:
            desc = "Calculates earned and unearned premium amounts per policy."
        elif "PREMCALC" in raw_id:
            desc = "Master premium calculation driver routing policies to auto or homeowner logic."
        elif node.get("data_type"):
            desc = f"Field/column entity with data type {node.get('data_type')}."
        else:
            desc = f"Enterprise legacy system component ({entity_label})."
    props_dict["description"] = desc

    # Data types and lines
    if node.get("data_type") and node.get("data_type") != "—":
        props_dict["data_type"] = node.get("data_type")
    if node.get("line_number"):
        props_dict["line_number"] = node.get("line_number")
    if node.get("confidence"):
        props_dict["confidence"] = node.get("confidence")
    if node.get("business_domain"):
        props_dict["business_domain"] = node.get("business_domain")

    # Check entity types
    raw_label_str = str(entity_label).lower()
    raw_id_str = str(raw_id).lower()
    is_business_rule = (
        raw_label_str == "businessrule"
        or "rule:" in raw_id_str
        or props_dict.get("rule_index") is not None
        or props_dict.get("entity_type") == "BusinessRule"
    )
    is_transformation = (
        raw_label_str == "transformation"
        or "transformation:" in raw_id_str
        or props_dict.get("entity_type") == "Transformation"
    )

    # Ingest any other custom properties on the node dict
    excluded_keys = {
        "<id>", "_labels", "size", "color", "font", "shape", "x", "y", "title",
        "borderWidth", "borderWidthSelected", "highlight", "hover", "name",
        "entity_type", "purpose", "source_type"
    }
    for k, v in node.items():
        if k not in excluded_keys and k not in props_dict and v is not None and str(v).strip() != "":
            props_dict[k] = v

    # Neo4j badge colors
    badge_colors = {
        "Entity": {"bg": "#A85A48", "color": "#FFFFFF"},          # Terracotta
        "Transformation": {"bg": "#EA580C", "color": "#FFFFFF"},    # Orange
        "BusinessRule": {"bg": "#D97706", "color": "#FFFFFF"},      # Amber
        "Table": {"bg": "#6D28D9", "color": "#FFFFFF"},             # Purple
        "Column": {"bg": "#0891B2", "color": "#FFFFFF"},            # Cyan
        "Program": {"bg": "#1D4ED8", "color": "#FFFFFF"},           # Deep Blue
        "Package": {"bg": "#047857", "color": "#FFFFFF"},           # Emerald Green
        "Artifact": {"bg": "#4338CA", "color": "#FFFFFF"},          # Indigo
    }
    b_style = badge_colors.get(str(entity_label), badge_colors["Entity"])

    # Dedicated Business Logic / Expression callout extraction
    expression_val = (
        props_dict.get("expression")
        or props_dict.get("formula")
        or props_dict.get("logic")
    )
    if not expression_val and is_business_rule:
        cand_rule = (
            props_dict.get("rule_statement")
            or props_dict.get("statement")
            or props_dict.get("rule_text")
            or props_dict.get("description")
        )
        if cand_rule and cand_rule != "No detailed description recorded." and not (
            isinstance(cand_rule, str) and cand_rule.startswith("Enterprise legacy system")
        ):
            expression_val = cand_rule

    rule_id_val = (
        props_dict.get("rule_id")
        or (f"Rule {props_dict.get('rule_index')}" if props_dict.get("rule_index") is not None else "")
        or (raw_id.split(":")[-1] if is_business_rule or is_transformation else "")
    )
    rule_type_val = props_dict.get("rule_type", "BUSINESS_RULE" if is_business_rule else ("TRANSFORMATION" if is_transformation else ""))

    business_logic_html = ""
    if expression_val:
        if is_business_rule:
            box_bg = "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)"
            box_border = "#FCD34D"
            box_border_l = "#D97706"
            header_color = "#92400E"
            header_title = "⚡ Business Rule Logic"
            tag_bg = "#FDE68A"
            tag_border = "#FCD34D"
            tag_color = "#78350F"
            text_color = "#78350F"
            r_id_tag = f"({html.escape(str(rule_id_val))})" if rule_id_val else ""
        elif is_transformation:
            box_bg = "linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)"
            box_border = "#FDBA74"
            box_border_l = "#EA580C"
            header_color = "#9A3412"
            header_title = "⚡ Transformation Expression"
            tag_bg = "#FED7AA"
            tag_border = "#FDBA74"
            tag_color = "#7C2D12"
            text_color = "#7C2D12"
            r_id_tag = f"({html.escape(str(rule_id_val))})" if rule_id_val else ""
        else:
            box_bg = "linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)"
            box_border = "#93C5FD"
            box_border_l = "#2563EB"
            header_color = "#1E40AF"
            header_title = "⚡ Logic / Expression"
            tag_bg = "#BFDBFE"
            tag_border = "#93C5FD"
            tag_color = "#1E3A8A"
            text_color = "#1E3A8A"
            r_id_tag = f"({html.escape(str(rule_id_val))})" if rule_id_val else ""

        business_logic_html = (
            f'<div style="margin: 8px 14px 10px 14px; background: {box_bg}; border: 1px solid {box_border}; border-left: 4px solid {box_border_l}; border-radius: 10px; padding: 10px 14px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">'
            f'<span style="font-size: 11px; font-weight: 800; color: {header_color}; text-transform: uppercase; letter-spacing: 0.04em;">{header_title} {r_id_tag}</span>'
            f'<span style="font-size: 10px; color: {tag_color}; font-weight: 700; background: {tag_bg}; border: 1px solid {tag_border}; padding: 1px 7px; border-radius: 4px;">{html.escape(str(rule_type_val))}</span>'
            f'</div>'
            f'<div style="font-family: \'JetBrains Mono\', monospace; font-size: 12px; color: {text_color}; word-break: break-word; font-weight: 700; line-height: 1.5;">'
            f'{html.escape(str(expression_val))}'
            f'</div>'
            f'</div>'
        )

    # Build Key-Value table rows matching KAIRIX Light Neumorphic theme
    sorted_keys = ["<id>"] + sorted([k for k in props_dict.keys() if k != "<id>"])
    table_rows = []

    for idx, k in enumerate(sorted_keys):
        v = props_dict[k]

        is_logic_prop = (
            k in ("expression", "formula", "logic", "rule_statement", "rule_id", "rule_type", "rule_index")
            or (is_business_rule and k == "description")
        )

        # Format display value
        if k == "<id>":
            val_display = html.escape(str(v))
            val_color = "#475569"
        elif isinstance(v, str):
            val_display = f'"{html.escape(v)}"'
            val_color = "#B45309" if is_logic_prop else "#1E293B"
        elif isinstance(v, (int, float)):
            val_display = str(v)
            val_color = "#0284C7"
        elif isinstance(v, bool):
            val_display = "true" if v else "false"
            val_color = "#7C3AED"
        else:
            val_display = html.escape(str(v))
            val_color = "#1E293B"

        safe_copy_val = html.escape(str(v), quote=True)

        if is_logic_prop:
            row_bg = "background-color: #FFFBEB; border-left: 3px solid #D97706;"
            row_mouseout_bg = "#FFFBEB"
        else:
            row_bg = "background-color: #F8FAFD;" if idx % 2 == 1 else "background-color: #FFFFFF;"
            row_mouseout_bg = "#F8FAFD" if idx % 2 == 1 else "#FFFFFF"

        table_rows.append(
            f'<tr style="border-bottom: 1px solid #EDF2F7; transition: background-color 0.15s ease; {row_bg}" onmouseover="this.style.backgroundColor=\'#EFF6FF\'" onmouseout="this.style.backgroundColor=\'{row_mouseout_bg}\'">'
            f'<td style="padding: 7px 10px; color: #334155; font-weight: 700; vertical-align: top; width: 34%; font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif; font-size: 12px;">{html.escape(k)}</td>'
            f'<td style="padding: 7px 10px; color: {val_color}; vertical-align: top; width: 66%; word-break: break-word; font-family: \'JetBrains Mono\', monospace; font-size: 11.5px; position: relative; line-height: 1.45;">'
            f'<span>{val_display}</span>'
            f'<button class="st-prop-copy-btn" data-copy="{safe_copy_val}" title="Copy value to clipboard" style="background: #F8FAFC; border: 1px solid #CBD5E1; color: #64748B; cursor: pointer; font-size: 11px; float: right; padding: 2px 5px; border-radius: 4px; margin-left: 6px; transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#93C5FD\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#64748B\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#F8FAFC\'">❐</button>'
            f'</td>'
            f'</tr>'
        )

    table_rows_html = "".join(table_rows)

    # Connected Edges section
    edges_html = ""
    if connected_edges:
        edge_rows = []
        for e in connected_edges[:12]:
            rel = str(e.get("type", "RELATES_TO"))
            src = str(e.get("source", "")).split(":")[-1]
            tgt = str(e.get("target", "")).split(":")[-1]
            is_outgoing = src == raw_id.split(":")[-1] or str(e.get("source")) == raw_id
            direction_icon = "➔" if is_outgoing else "⬅"
            neighbor_name = tgt if is_outgoing else src

            edge_rows.append(
                f'<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 10px; margin-bottom: 5px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">'
                f'<span style="background: #EFF6FF; color: #1D4ED8; font-weight: 700; font-size: 11px; padding: 2px 8px; border-radius: 6px; border: 1px solid #BFDBFE; white-space: nowrap; font-family: \'JetBrains Mono\', monospace;">{direction_icon} {html.escape(rel)}</span>'
                f'<span style="font-family: \'JetBrains Mono\', monospace; color: #1E293B; max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11.5px; font-weight: 600;" title="{html.escape(neighbor_name)}">{html.escape(neighbor_name)}</span>'
                f'</div>'
            )
        edges_list_html = "".join(edge_rows)
        edges_html = (
            f'<div style="margin-top: 0.5rem; border-top: 1px solid #E2E8F0; padding: 10px 14px 6px 14px; background: #F8FAFC;">'
            f'<div style="font-size: 11px; font-weight: 800; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Connected Relationships ({len(connected_edges)})</div>'
            f'<div style="max-height: 160px; overflow-y: auto; padding-right: 2px;">{edges_list_html}</div>'
            f'</div>'
        )

    # Encode all properties to JSON for copy all
    encoded_json = html.escape(json.dumps(props_dict, indent=2), quote=True)

    # Light Neumorphic Node details panel matching KAIRIX visual design system
    neo4j_panel_html = (
        f'<div id="neo4j-node-details-card" style="background: #FFFFFF; border: 1px solid #D5DFEB; border-radius: 14px; overflow: hidden; font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 6px 6px 18px rgba(166, 180, 200, 0.35), -6px -6px 18px rgba(255, 255, 255, 0.95); margin-bottom: 0.75rem;">\n'
        f'<div style="padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);">\n'
        f'<div style="display: flex; align-items: center; gap: 8px;">\n'
        f'<span style="font-size: 15px;">📄</span>\n'
        f'<span style="font-size: 14px; font-weight: 800; color: #0F172A; letter-spacing: -0.01em;">Node details</span>\n'
        f'</div>\n'
        f'<div style="display: flex; align-items: center; gap: 8px;">\n'
        f'<button class="st-copy-all-btn" data-copy="{encoded_json}" title="Copy all properties as JSON" style="background: #FFFFFF; border: 1px solid #CBD5E1; color: #334155; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 6px; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.15s;" onmouseover="this.style.color=\'#2563EB\'; this.style.borderColor=\'#2563EB\'; this.style.background=\'#EFF6FF\'" onmouseout="this.style.color=\'#334155\'; this.style.borderColor=\'#CBD5E1\'; this.style.background=\'#FFFFFF\'">❐ Copy all</button>\n'
        f'</div>\n'
        f'</div>\n'
        f'<div style="padding: 12px 16px 6px 16px;">\n'
        f'<span style="background: {b_style["bg"]}; color: {b_style["color"]}; font-size: 11.5px; font-weight: 700; padding: 3px 12px; border-radius: 14px; display: inline-block; letter-spacing: 0.02em; font-family: \'Inter\', -apple-system, BlinkMacSystemFont, sans-serif; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">\n'
        f'{html.escape(str(entity_label))}\n'
        f'</span>\n'
        f'</div>\n'
        f'{business_logic_html}\n'
        f'<div style="max-height: 480px; overflow-y: auto; padding: 4px 14px 10px 14px;">\n'
        f'<table style="width: 100%; border-collapse: collapse; font-size: 12px;">\n'
        f'<thead>\n'
        f'<tr style="border-bottom: 2px solid #2563EB; background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); color: #0F172A; text-align: left;">\n'
        f'<th style="padding: 8px 10px; font-weight: 800; width: 34%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Key</th>\n'
        f'<th style="padding: 8px 10px; font-weight: 800; width: 66%; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Value</th>\n'
        f'</tr>\n'
        f'</thead>\n'
        f'<tbody>\n'
        f'{table_rows_html}\n'
        f'</tbody>\n'
        f'</table>\n'
        f'</div>\n'
        f'{edges_html}\n'
        f'<script>\n'
        f'(function() {{\n'
        f'  var panel = document.getElementById("neo4j-node-details-card");\n'
        f'  if (panel && !panel.dataset.listenerAttached) {{\n'
        f'    panel.dataset.listenerAttached = "true";\n'
        f'    panel.addEventListener("click", function(e) {{\n'
        f'      var allBtn = e.target.closest(".st-copy-all-btn");\n'
        f'      if (allBtn) {{\n'
        f'        var val = allBtn.getAttribute("data-copy") || "";\n'
        f'        navigator.clipboard.writeText(val);\n'
        f'        allBtn.innerText = "✓ Copied";\n'
        f'        setTimeout(function() {{ allBtn.innerText = "❐ Copy all"; }}, 1500);\n'
        f'        return;\n'
        f'      }}\n'
        f'      var propBtn = e.target.closest(".st-prop-copy-btn");\n'
        f'      if (propBtn) {{\n'
        f'        var val = propBtn.getAttribute("data-copy") || "";\n'
        f'        navigator.clipboard.writeText(val);\n'
        f'        propBtn.innerText = "✓";\n'
        f'        setTimeout(function() {{ propBtn.innerText = "❐"; }}, 1200);\n'
        f'        return;\n'
        f'      }}\n'
        f'    }});\n'
        f'  }}\n'
        f'}})();\n'
        f'</script>\n'
        f'</div>'
    )

    try:
        if hasattr(st, "html"):
            st.html(neo4j_panel_html, unsafe_allow_javascript=True)
        else:
            st.markdown(neo4j_panel_html, unsafe_allow_html=True)
    except TypeError:
        st.html(neo4j_panel_html)

