import json

transcript_path = r"C:\Users\rohit\.gemini\antigravity\brain\f18e9b59-555e-4625-bc0c-9d3993a2260b\.system_generated\logs\transcript.jsonl"

inputs = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                inputs.append((data.get("step_index"), data.get("content", "")[:100]))
        except Exception:
            pass

for idx, content in inputs:
    print(f"Step {idx}: {content}")
