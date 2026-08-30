import os
import re

repo_root = r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent"

secret_patterns = [
    r"AIzaSy[A-Za-z0-9_-]{33}",
    r"key=[A-Za-z0-9_-]{20,}",
    r"\"api_key\"\s*:\s*\"[A-Za-z0-9_-]{20,}\""
]

exposed_secrets = []

for root, dirs, files in os.walk(repo_root):
    if ".git" in root or "__pycache__" in root or ".venv" in root:
        continue
    for fname in files:
        if fname.endswith((".py", ".json", ".md", ".env", ".log", ".txt")):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for pat in secret_patterns:
                    matches = re.findall(pat, content)
                    if matches:
                        exposed_secrets.append((os.path.relpath(fpath, repo_root), len(matches)))
            except Exception as e:
                pass

print("==========================================")
print("SECURITY & SECRET EXPOSURE AUDIT")
print("==========================================")
if exposed_secrets:
    print(f"[ALERT] POTENTIAL SECRETS DETECTED IN {len(exposed_secrets)} FILES:")
    for path, count in exposed_secrets:
        print(f"   -> File: {path} ({count} occurrences)")
else:
    print("[PASSED] ZERO exposed API keys or secrets detected in repository files.")

print("\n--- Environment Key Check ---")
api_key_env = os.environ.get("GEMINI_API_KEY")
print("GEMINI_API_KEY in os.environ:", "PRESENT (hidden)" if api_key_env else "NOT SET")
print("RUN_REAL_LLM_TESTS in os.environ:", os.environ.get("RUN_REAL_LLM_TESTS", "NOT SET"))
