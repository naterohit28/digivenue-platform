import json
import os

transcript_path = r"C:\Users\rohit\.gemini\antigravity\brain\f18e9b59-555e-4625-bc0c-9d3993a2260b\.system_generated\logs\transcript.jsonl"
output_path = r"C:\Users\rohit\Downloads\DigiStories\last_user_request.txt"

try:
    if os.path.exists(transcript_path):
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("type") == "USER_INPUT":
                        content = data.get("content", "")
                        if "UNIFIED MASTER UPGRADE PROMPT" in content:
                            with open(output_path, "w", encoding="utf-8") as out:
                                out.write(content)
                            print("Success! Extracted prompt to:", output_path)
                except Exception as ex:
                    pass
    else:
        print("Transcript path does not exist:", transcript_path)
except Exception as e:
    print("Error:", e)
