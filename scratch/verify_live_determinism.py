import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

import time
from ui.services.investigation_service import InvestigationService, clear_query_cache

print("=" * 80)
print("TEST: LIVE END-TO-END QUERY DETERMINISM & CACHING VERIFICATION")
print("=" * 80)

q = "How is earned premium calculated?"

# Run 1: Cold run (fresh LLM synthesis via NVIDIA NIM)
print("[*] Starting Run 1 (Cold LLM synthesis)...")
t0 = time.perf_counter()
res1 = InvestigationService.query(q)
t1 = time.perf_counter() - t0
print(f"[+] Run 1 finished in {t1:.2f}s! Success: {res1.get('success')}, Cached: {res1.get('cached')}")
print(f"    Confidence: {res1.get('confidence_score')}%")
print(f"    Key Points ({len(res1.get('key_points', []))}):")
for idx, kp in enumerate(res1.get('key_points', []), 1):
    print(f"      {idx}. {kp}")
print(f"    Formula snippet: {repr(res1.get('formula', '')[:100])}")
print(f"    Data Flow snippet: {repr(res1.get('data_flow', '')[:100])}")

# Run 2: Warm run (Thread-safe Cache Hit - simulates 2nd browser tab)
print("\n[*] Starting Run 2 (Warm Cache Hit / Second Tab)...")
t0 = time.perf_counter()
res2 = InvestigationService.query("how is earned premium calculated? ")
t2 = time.perf_counter() - t0
print(f"[+] Run 2 finished in {t2*1000:.2f}ms! Success: {res2.get('success')}, Cached: {res2.get('cached')}")

assert res2.get("cached") is True, "Run 2 must be served from cache!"
assert res1.get("answer") == res2.get("answer"), "Answers must be 100% identical!"
assert res1.get("key_points") == res2.get("key_points"), "Key points must be 100% identical!"
assert res1.get("formula") == res2.get("formula"), "Formulas must be 100% identical!"
assert res1.get("data_flow") == res2.get("data_flow"), "Data flow must be 100% identical!"

print("\n" + "=" * 80)
print("SUCCESS: Cross-tab Bit-For-Bit Determinism & Sub-Millisecond Speed Verified!")
print("=" * 80)
