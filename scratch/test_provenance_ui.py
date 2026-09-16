import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

from ui.components.answer_panel import _render_data_flow

test_dataflow = (
    "PI‑EFFECTIVE‑DATE ➔ "
    "VALIDATE‑DATES (date validation) ➔ "
    "CALCULATE‑EARNED (compute WS‑EFF‑INT, WS‑EXP‑INT, WS‑CALC‑INT) ➔ "
    "WS‑TERM‑DAYS ➔ "
    "WS‑EARNED‑DAYS ➔ "
    "WS‑EARNED formula ➔ "
    "cap WS‑EARNED ➔ "
    "compute WS‑UNEARNED ➔ "
    "zero negative) ➔ "
    "WRITE‑RESULT (MOVE WS‑EARNED TO PRO‑EARNED‑PREMIUM, MOVE WS‑UNEARNED TO PRO‑UNEARNED‑PREMIUM) ➔ "
    "PRO‑REC output file"
)

html_out = _render_data_flow(test_dataflow)

print("=" * 80)
print("TESTING RENDER DATA FLOW WITH PROVENANCE CHIPS")
print("=" * 80)
print(f"Total HTML Size: {len(html_out)} bytes")
print("Steps count (df-step-item):", html_out.count("df-step-item"))
print("File chips count (df-file-chip):", html_out.count("df-file-chip"))
print("EARNPREM.CBL occurrences:", html_out.count("EARNPREM.CBL"))

# Critical checks
assert html_out.count("df-step-item") == 11, f"Expected 11 steps, got {html_out.count('df-step-item')}"
assert html_out.count("df-file-chip") == 11, f"Expected 11 file chips, got {html_out.count('df-file-chip')}"
assert "Line 559" in html_out, "Line 559 (CALCULATE-EARNED) must be in output!"
assert "Line 611" in html_out, "Line 611 (WS-EARNED formula) must be in output!"
assert "Line 617" in html_out, "Line 617 (cap WS-EARNED) must be in output!"

for idx, line in enumerate(html_out.splitlines(), 1):
    assert not line.startswith("    "), f"Line {idx} has leading 4 spaces!"

print("\n[+] ALL CHECKS PASSED: 11/11 Steps have clean filename & line number chips rendered!")
