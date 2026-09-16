import sys
import json
sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from investigation_agent.agent import InvestigationAgent

question = "How is earned premium calculated?"
print("=" * 80)
print(f"QUERY: {question}")
print("=" * 80)

agent = InvestigationAgent()

def on_progress(stage, msg):
    print(f"[*] {msg}")

result = agent.ask(question, on_progress=on_progress)

print("\n" + "=" * 80)
print("PHASE 1: CLASSIFIED INTENT")
print("=" * 80)
print(f"Intent: {result.intent}")

print("\n" + "=" * 80)
print(f"PHASE 2A: GRAPH EVIDENCE FROM NEO4J ({len(result.graph_evidence)} records)")
print("=" * 80)
for i, g in enumerate(result.graph_evidence, 1):
    try:
        parsed = json.loads(g)
        print(f"\n[Graph Evidence #{i}]:")
        for k, v in parsed.items():
            print(f"  {k}: {v}")
    except Exception:
        print(f"\n[Graph Evidence #{i}]: {g}")

print("\n" + "=" * 80)
print(f"PHASE 2B: VECTOR EVIDENCE FROM PINECONE ({len(result.vector_evidence)} chunks)")
print("=" * 80)
for i, v in enumerate(result.vector_evidence, 1):
    print(f"\n[Vector Chunk #{i}]:")
    print(v)

print("\n" + "=" * 80)
print("PHASE 4: FINAL SYNTHESIZED ANSWER & CONFIDENCE")
print("=" * 80)
print(f"Confidence Score: {result.confidence * 100:.1f}%")
print(f"Referenced Source Files: {result.source_files}")
print("\nANSWER CONTENT:")
print(result.answer)
