import os
import time
import json
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv(override=False)

api_key = os.getenv("NVIDIA_NIM_API_KEY")
candidates = [
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "nv-mistralai/mistral-nemo-12b-instruct",
    "mistralai/codestral-22b-instruct-v0.1",
    "mistralai/mistral-7b-instruct-v0.3",
    "nvidia/llama3-chatqa-1.5-70b",
]

for m in candidates:
    t0 = time.time()
    try:
        req = Request(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            data=json.dumps({
                "model": m,
                "messages": [{"role": "user", "content": "Explain earned premium in 1 sentence."}],
                "max_tokens": 60,
                "temperature": 0.1,
            }).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            content = data["choices"][0]["message"]["content"].strip()
            print(f"[OK] {m}: {time.time()-t0:.2f}s -> {content[:80]}...")
    except Exception as e:
        print(f"[FAIL] {m}: {time.time()-t0:.2f}s -> {e}")
