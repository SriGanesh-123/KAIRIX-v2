import re

flow_text = "PRI-WRITTEN-PREMIUM (premium record) ➔ CALCULATE-EARNED (compute WS-EFF-INT, WS-EXP-INT, WS-CALC-INT, WS-TERM-DAYS, WS-EARNED-DAYS) ➔ WS-EARNED = PRI-WRITTEN-PREMIUM * WS-EARNED-DAYS / WS-TERM-DAYS (T7) ➔ Cap WS-EARNED (T8) ➔ WS-UNEARNED = PRI-WRITTEN-PREMIUM - WS-EARNED (T9) ➔ Negative guard (T10) ➔ WRITE-RESULT (MOVE WS-EARNED TO PRO-EARNED-PREMIUM; MOVE WS-UNEARNED TO PRO-UNEARNED-PREMIUM) ➔ PRO-EARNED-PREMIUM output ➔ (optional) RPTEXTRACT.CBL: MOVE EARNED-PREMIUM TO RPT-EARNED-PREM (T9) for reporting."

steps = [s.strip() for s in re.split(r"\s*(?:➔|→|➜|➡|➤|->|-->|=>|\n)\s*", flow_text) if s.strip()]

print(f"Total steps found: {len(steps)}")
for i, s in enumerate(steps, 1):
    print(f"{i}: {s}")
