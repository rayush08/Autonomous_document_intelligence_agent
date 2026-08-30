import os

repo_root = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent"
possible_files = [".env", ".env.local", "config.py", "key.txt", "secrets.json"]

found = []
for p in possible_files:
    full_p = os.path.join(repo_root, p)
    if os.path.exists(full_p):
        found.append(p)

print("Found config files in repo root:", found)
