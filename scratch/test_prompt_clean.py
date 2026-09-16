import os
import sys
import time
import re
import json
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv(override=False)

api_key = os.getenv("NVIDIA_NIM_API_KEY")

prompt = """You are a senior insurance legacy systems reverse-engineering specialist.
Retrieved Evidence:
- EARNPREM.CBL: COMPUTE WS-EARNED-PREM = WS-WRITTEN-PREM * WS-EARNED-DAYS / WS-TERM-DAYS.
- EARNPREM.CBL: Term days = Expiry Date - Effective Date + 1.
- EARNPREM.CBL: Unearned premium = Written - Earned (min 0).

Question: How is earned premium calculated in EARNPREM.CBL?

CRITICAL: Do NOT write any thinking process, reasoning steps, internal thoughts, or preamble.
Start your response IMMEDIATELY with the word "ANSWER".

REQUIRED FORMAT:
ANSWER
[Direct answer]

KEY POINTS
- [Point 1]
- [Point 2]

FORMULA
[Formula]

SOURCES
[Sources]

CONFIDENCE
[High - 90%]
"""

sys_prompt = "You are a senior insurance legacy systems reverse-engineering specialist. Respond strictly following the format. Do NOT generate internal thinking."

t0 = time.time()
req = Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=json.dumps({
        "model": "nvidia/nemotron-3-super-120b-a12b",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 800,
    }).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST",
)

with urlopen(req, timeout=30) as res:
    data = json.loads(res.read().decode())
    raw = data["choices"][0]["message"]["content"]
    print(f"Completed in {time.time()-t0:.2f}s!")
    print("--- RAW OUTPUT ---")
    print(raw[:500])
