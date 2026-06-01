import json

transcript_path = r"C:\Users\rohit\.gemini\antigravity\brain\f18e9b59-555e-4625-bc0c-9d3993a2260b\.system_generated\logs\transcript.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("step_index") == 645:
                print("Step index 645 found.")
                content = data.get("content", "")
                print("Length of content:", len(content))
                print("Content starts with:")
                print(content[:500])
                print("Content ends with:")
                print(content[-500:])
        except Exception as e:
            pass
