import os

home = os.path.expanduser("~")
candidates = [
    os.path.join(home, ".env"),
    os.path.join(home, ".gemini", ".env"),
    os.path.join(home, ".gemini", "antigravity", ".env"),
    os.path.join(home, ".gemini", "config", ".env"),
]

print("=== SAFE FILE EXISTENCE CHECK ===")
for p in candidates:
    print(f"Path '{p}': {os.path.exists(p)}")
