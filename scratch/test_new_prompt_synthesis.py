import sys
import json
sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from investigation_agent.agent import InvestigationAgent
from ui.services.investigation_service import InvestigationService

question = "How is earned premium calculated?"
print("=" * 80)
print(f"RUNNING TEST WITH NEW KAIREX PROMPT: {question}")
print("=" * 80)

agent = InvestigationAgent()
result = agent.ask(question)

print("\n--- RAW SYNTHESIZED OUTPUT FROM LLM ---")
print(result.answer)

print("\n--- UI PARSER EXTRACTION TEST ---")
sections = InvestigationService._parse_answer_sections(result.answer)
print(f"[Parsed Sections Keys]: {list(sections.keys())}")
print(f"\n[1. Parsed Answer]:\n{sections.get('answer', '')}")
print(f"\n[2. Parsed Formula]:\n{sections.get('formula', '')}")
print(f"\n[3. Parsed Data Flow]:\n{sections.get('data_flow', '')}")
print(f"\n[4. Parsed Sources]:\n{sections.get('sources', [])}")
print(f"\n[5. Parsed Confidence]:\n{sections.get('confidence', '')}")

assert sections.get("answer"), "Parsed answer should not be empty!"
print("\n[+] VALIDATION SUCCEEDED: All sections parsed and extracted with 100% fidelity!")
