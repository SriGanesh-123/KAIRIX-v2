import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, ".")
import re
from ui.components.answer_panel import _render_data_flow

key_points = [
    "Product type must be 'AU' (auto); otherwise error P004 is raised (PREMCALC.CBL validation).",
    "Auto policies require a matching vehicle record; missing record triggers error P002 (PREMCALC.CBL GET-VEHICLE).",
    "For CommercialPackage policies, Written_Premium = ISNULL(SUM(amount),0) from pcx_ca7transaction where BranchID = pp.id when PatternCode = 'ca7line' (PolicyCenter_CPP_Breakdown.sql T015).",
    "PatternCode 'ca7line' is mapped to the human-readable LineOfBusiness 'Commercial Auto Line' (PolicyCenter_CPP_Breakdown.sql T012 / PolicyCenter_Monoline.sql T1).",
    "Rows where ProductCode = 'CommercialPackage' AND LineOfBusiness = 'C.P.P.' are excluded (PolicyCenter_CPP_Breakdown.sql T017)."
]

flow_steps = []
for kp in key_points:
    # Look for parenthetical citation like (PREMCALC.CBL GET-VEHICLE) or (PolicyCenter_CPP_Breakdown.sql T015)
    m_paren = re.search(r'\(([^)]+\.(?:cbl|sql|dtsx)[^)]*)\)\s*$', kp, re.IGNORECASE)
    if m_paren:
        ref = m_paren.group(1).strip()
        desc = kp[:m_paren.start()].strip()
    else:
        m_file = re.search(r'\b([A-Za-z0-9_\-]+\.(?:CBL|cob|cpy|dtsx|sql))\b', kp, re.IGNORECASE)
        m_task = re.search(r'\b(T\d{1,4}|GET-[A-Z0-9_\-]+|VALIDATE-[A-Z0-9_\-]+|CALCULATE-[A-Z0-9_\-]+|OPEN-[A-Z0-9_\-]+)\b', kp, re.IGNORECASE)
        ref = f"{m_file.group(1)}:{m_task.group(1)}" if (m_file and m_task) else (m_file.group(1) if m_file else None)
        desc = kp

    if ref:
        flow_steps.append(f"[{ref}] {desc}")
    else:
        flow_steps.append(desc)

flow_str = " ➔ ".join(flow_steps)
print("Flow string:")
print(flow_str)
print("\n" + "="*80)
print("Rendering via _render_data_flow:")
print("="*80)
html_out = _render_data_flow(flow_str)
print("Rendered HTML size:", len(html_out))
for line in html_out.splitlines():
    if "df-step-num" in line or "df-chip-file" in line or "df-card-title" in line:
        print(" ", line.strip())
