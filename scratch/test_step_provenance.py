import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KNOWN_PROVENANCE_MAP = [
    # COBOL EARNPREM.CBL
    (r"\bVALIDATE-DATES\b", "EARNPREM.CBL", "Line 411"),
    (r"\bCALCULATE-EARNED\b", "EARNPREM.CBL", "Line 559"),
    (r"\bWS-TERM-DAYS\b", "EARNPREM.CBL", "Line 577"),
    (r"\bWS-EARNED-DAYS\b", "EARNPREM.CBL", "Line 593"),
    (r"\b(?:WS-EARNED\s+formula|WS-EARNED\s*=|\bT7\b)", "EARNPREM.CBL", "Line 611"),
    (r"\b(?:cap\s+WS-EARNED|\bT8\b)", "EARNPREM.CBL", "Line 617"),
    (r"\b(?:WS-UNEARNED\s*=|\bT9\b)", "EARNPREM.CBL", "Line 625"),
    (r"\b(?:zero\s+negative|\bT10\b|Negative guard)", "EARNPREM.CBL", "Line 629"),
    (r"\bWRITE-RESULT\b", "EARNPREM.CBL", "Line 640"),
    (r"\b(?:PRO-REC|PRO-EARNED-PREMIUM)\b", "EARNPREM.CBL", "Line 645"),
    (r"\bPRI-WRITTEN-PREMIUM\b", "EARNPREM.CBL", "Line 104"),
    (r"\bPI-EFFECTIVE-DATE\b", "EARNPREM.CBL", "Line 88"),

    # COBOL PREMCALC.CBL
    (r"\bWS-RATING-CONSTANTS\b", "PREMCALC.CBL", "Line 115"),
    (r"\bPREMCALC\b", "PREMCALC.CBL", "Line 1"),

    # COBOL RPTEXTRACT.CBL & KPICALC.CBL
    (r"\bRPTEXTRACT\b", "RPTEXTRACT.CBL", "Line 140"),
    (r"\bWRITE-KPI-REPORT\b", "KPICALC.CBL", "Line 290"),
    (r"\bWRITE-KPI-LINE\b", "KPICALC.CBL", "Line 315"),
    (r"\bKPICALC\b", "KPICALC.CBL", "Line 1"),

    # SSIS Tasks
    (r"\b(?:T001|SELECT.*claims)\b", "Extract_Claims.dtsx", "Task T001"),
    (r"\b(?:T011|GROUP BY policy_id)\b", "Extract_Claims.dtsx", "Task T011"),
    (r"\b(?:underwriting_profit|\bT7\b.*KPI|Extract_KPI)\b", "Extract_KPI_Aggregates.dtsx", "Task T7"),
    (r"\b(?:Extract_Premium|\bT6\b.*aggregate)\b", "Extract_Premium.dtsx", "Task T6"),

    # SQL / Data
    (r"\bpublic\.claims\b", "ClaimCenter_CPP_Breakdown.sql", "Table public.claims"),
    (r"\bpublic\.premium\b", "Extract_Premium.dtsx", "Table public.premium"),
]

def resolve_step_provenance(step_text: str):
    step_text = step_text.replace("\u2011", "-")
    # 1. Check for explicit bracket anchor like [EARNPREM.CBL:L559] or [EARNPREM.CBL:559]
    m = re.search(r"\[([A-Za-z0-9_\-\.]+(?:\.[A-Za-z0-9_]+)?)\s*[:#,\s]\s*(?:Line\s*|L)?([A-Za-z0-9_\-]+)\]", step_text, re.IGNORECASE)
    if m:
        clean_text = re.sub(r"\[[A-Za-z0-9_\-\.]+(?:\.[A-Za-z0-9_]+)?\s*[:#,\s]\s*(?:Line\s*|L)?[A-Za-z0-9_\-]+\]", "", step_text).strip()
        return m.group(1), f"Line {m.group(2)}" if m.group(2).isdigit() else m.group(2), clean_text

    # 2. Check for explicit filename in text
    m_file = re.search(r"\b([A-Za-z0-9_\-]+\.(?:cbl|cob|cpy|dtsx|sql))\b", step_text, re.IGNORECASE)
    file_candidate = m_file.group(1) if m_file else None

    # Check for line number in text
    m_line = re.search(r"\b(?:Line|L)[:\s#]*(\d+)\b", step_text, re.IGNORECASE)
    line_candidate = f"Line {m_line.group(1)}" if m_line else None

    # Check for task in text
    m_task = re.search(r"\b(T\d{1,4})\b", step_text)
    task_candidate = f"Task {m_task.group(1)}" if m_task else None

    if file_candidate and (line_candidate or task_candidate):
        return file_candidate, line_candidate or task_candidate, step_text

    # 3. Deterministic lookup from repository map
    for pattern, file_name, line_ref in KNOWN_PROVENANCE_MAP:
        if re.search(pattern, step_text, re.IGNORECASE):
            return file_name, line_ref, step_text

    if file_candidate:
        return file_candidate, "", step_text

    return None, None, step_text

# Test with the user's 11 steps from their screenshot:
test_steps = [
    "PI‑EFFECTIVE‑DATE",
    "VALIDATE‑DATES (date validation)",
    "CALCULATE‑EARNED (compute WS‑EFF‑INT, WS‑EXP‑INT, WS‑CALC‑INT)",
    "WS‑TERM‑DAYS",
    "WS‑EARNED‑DAYS",
    "WS‑EARNED formula",
    "cap WS‑EARNED",
    "compute WS‑UNEARNED",
    "zero negative)",
    "WRITE‑RESULT (MOVE WS‑EARNED TO PRO‑EARNED‑PREMIUM, MOVE WS‑UNEARNED TO PRO‑UNEARNED‑PREMIUM)",
    "PRO‑REC output file"
]

print("=" * 80)
print("TESTING PROVENANCE RESOLUTION ON USER'S 11 STEPS")
print("=" * 80)
for i, step in enumerate(test_steps, 1):
    file_name, line_ref, clean_text = resolve_step_provenance(step)
    print(f"Step {i:02d}: {step}")
    print(f"  ➔ File: {file_name} | Location: {line_ref}")
