import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

from ui.services.investigation_service import InvestigationService
from ui.components.answer_panel import _render_data_flow

raw_output_without_keypoints = """
**ANSWER:**
The earned premium logic resides in the COBOL program **EARNPREM.CBL**, specifically within the `CALCULATE-EARNED` paragraph where the premium is calculated, capped, and then written out via the `WRITE-RESULT` paragraph.

**DATA FLOW PIPELINE:**
PRI-WRITTEN-PREMIUM (premium record) ➔ CALCULATE-EARNED (compute WS-EFF-INT, WS-EXP-INT, WS-CALC-INT, WS-TERM-DAYS, WS-EARNED-DAYS) ➔ WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS (T7) ➔ Cap WS-EARNED (T8) ➔ WS-UNEARNED = PRI-WRITTEN-PREMIUM - WS-EARNED (T9) ➔ Negative guard (T10) ➔ WRITE-RESULT (MOVE WS-EARNED TO PRO-EARNED-PREMIUM; MOVE WS-UNEARNED TO PRO-UNEARNED-PREMIUM) ➔ PRO-EARNED-PREMIUM output ➔ (optional) RPTEXTRACT.CBL: MOVE EARNED-PREMIUM TO RPT-EARNED-PREM (T9) for reporting.

**EXACT LOGIC / MATHEMATICAL FORMULA:**
WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS (Transformation T7)
IF WS-EARNED > PRI-WRITTEN-PREMIUM THEN WS-EARNED = PRI-WRITTEN-PREMIUM (Transformation T8)

**VERIFIED SOURCES:**
- EARNPREM.CBL
- RPTEXTRACT.CBL

**CONFIDENCE SCORE:** 95%
"""

print("=" * 80)
print("TEST 1: PARSER & KEY POINTS FALLBACK VERIFICATION")
print("=" * 80)
parsed = InvestigationService._parse_answer_sections(raw_output_without_keypoints)
print(f"Parsed keys: {list(parsed.keys())}")
print(f"Key points count: {len(parsed['key_points'])}")
for i, kp in enumerate(parsed['key_points'], 1):
    print(f"  {i}. {kp}")
assert len(parsed['key_points']) > 0, "Key points should NOT be empty even if missing in raw LLM output!"
print("[+] Test 1 Passed: Key points successfully extracted!")

print("\n" + "=" * 80)
print("TEST 2: PIPELINE HTML RENDERING VERIFICATION")
print("=" * 80)
data_flow_text = parsed.get("data_flow", "")
pipeline_html = _render_data_flow(data_flow_text)

assert "df-pipeline-wrapper" in pipeline_html
assert "df-step-box" in pipeline_html
assert "09" in pipeline_html  # 9th step
assert "df-badge-cobol" in pipeline_html
assert "df-arrow-chevron" in pipeline_html

# CRITICAL CHECK: Verify that NO line has 4 or more leading spaces (which causes Streamlit code-block escaping)
for idx, line in enumerate(pipeline_html.splitlines(), 1):
    assert not line.startswith("    "), f"Line {idx} has 4+ leading spaces: {repr(line)} - this triggers markdown code-block bug!"

print(f"Generated HTML size: {len(pipeline_html)} bytes")
print("Total 'df-step-item' matches:", pipeline_html.count("df-step-item"))
assert pipeline_html.count("df-step-item") == 9
print("[+] Test 2 Passed: 9 connected steps cleanly generated with badges & chevrons (0 code-block indents)!")

raw_output_with_keypoints = """
**ANSWER:**
Earned premium is calculated pro-rata based on effective and expiry dates inside EARNPREM.CBL.

**KEY POINTS:**
- Calculation executes inside EARNPREM.CBL within CALCULATE-EARNED
- Cap transformation T8 guarantees earned premium does not exceed written premium
- RPTEXTRACT maps results to monthly executive reporting tables

**EXACT LOGIC / MATHEMATICAL FORMULA:**
WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS

**VERIFIED SOURCES:**
- EARNPREM.CBL
- RPTEXTRACT.CBL

**CONFIDENCE SCORE:** 95%
"""
print("\n" + "=" * 80)
print("TEST 3: PARSER WITH EXPLICIT KEY POINTS & DATAFLOW FALLBACK")
print("=" * 80)
parsed_explicit = InvestigationService._parse_answer_sections(raw_output_with_keypoints)
print("Explicit key points count:", len(parsed_explicit['key_points']))
for i, kp in enumerate(parsed_explicit['key_points'], 1):
    print(f"  {i}. {kp}")
assert len(parsed_explicit['key_points']) == 3

print("\nAuto-constructed Data Flow Fallback:")
print(parsed_explicit['data_flow'])
assert parsed_explicit['data_flow'], "Data flow should NOT be empty; fallback should populate it!"
fallback_html = _render_data_flow(parsed_explicit['data_flow'])
assert "df-pipeline-wrapper" in fallback_html
print("[+] Test 3 Passed: Explicit key points parsed AND missing dataflow auto-synthesized!")
