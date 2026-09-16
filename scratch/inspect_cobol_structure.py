import json

with open("output/cobol/EARNPREM_metadata.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print("PARAGRAPHS:")
paragraphs = d.get("paragraphs", [])
for p in paragraphs:
    print(f"  {p.get('name')}: lines {p.get('start_line')} to {p.get('end_line')}")

print("\nOPERATIONS BY PARAGRAPH:")
ops = d.get("operations", {})
for op_type, items in ops.items():
    if not items: continue
    print(f"\n  Operation: {op_type} ({len(items)} items)")
    for it in items[:3]:
        s_line = it.get("start_line")
        parent_p = "GLOBAL"
        for p in paragraphs:
            if p.get("start_line") <= s_line <= p.get("end_line"):
                parent_p = p.get("name")
                break
        print(f"    Line {s_line} (in {parent_p}): {it.get('text')[:80]}")

print("\nRECORDS & FIELDS:")
for r in d.get("records", [])[:4]:
    print(f"  Record: {r.get('name')} (lines {r.get('start_line')}-{r.get('end_line')})")
    for f in r.get("fields", [])[:3]:
        print(f"    - Field: {f.get('name')} ({f.get('picture')})")
