"""latency benchmark. Prints the median seconds per structured LLM call."""
import json
import time

import ollama

schema = {"type": "object",
          "properties": {"action": {"enum": ["retry", "modify", "replan"]}, "why": {"type": "string"}},
          "required": ["action", "why"]}
times = []
for i in range(10):
    t0 = time.time()
    r = ollama.chat(model="qwen2.5:7b",
                    messages=[{"role": "user", "content": "A robot grasp failed with PARAM_MISMATCH twice. Choose recovery."}],
                    format=schema, options={"temperature": 0.7, "seed": i, "num_ctx": 4096})
    times.append(time.time() - t0)
    print(i, round(times[-1], 2), "s")
print("median s/call:", sorted(times)[len(times) // 2], "| last output parses:", json.loads(r.message.content))
