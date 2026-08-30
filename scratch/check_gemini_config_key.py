import os

paths_to_check = [
    r"C:\Users\ayush\.gemini\config\mcp_config.json",
    r"C:\Users\ayush\.gemini\config\credentials.json",
    r"C:\Users\ayush\.gemini\antigravity\config.json"
]

for p in paths_to_check:
    if os.path.exists(p):
        print(f"File exists: {p}")
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"   Size: {len(content)} bytes")
        except Exception as e:
            print(f"   Error reading {p}: {e}")
    else:
        print(f"Not found: {p}")
