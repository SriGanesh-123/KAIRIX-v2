import os
import sys
import time
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.getcwd())
from dotenv import load_dotenv

load_dotenv(override=False)

os.environ["NIM_MODEL"] = "nvidia/nemotron-3-super-120b-a12b"

from investigation_agent.agent import InvestigationAgent

agent = InvestigationAgent()
t0 = time.time()
res = agent.ask("How is earned premium calculated in EARNPREM.CBL?")
print(f"Investigation completed in {time.time()-t0:.2f}s!")
print("\n--- ANSWER ---\n", res.answer)
