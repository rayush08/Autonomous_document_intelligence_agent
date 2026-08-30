import os
import re

files_to_check = [
    r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\src\llm\gemini_client.py",
    r"c:\Users\ayush\OneDrive\Documents\GitHub\autonomous_document_intelligence_agent\tests\test_gemini_client.py"
]

secret_patterns = [
    r"AIzaSy[A-Za-z0-9_-]{33}",
    r"key=[A-Za-z0-9_-]{20,}",
    r"\"api_key\"\s*:\s*\"[A-Za-z0-9_-]{20,}\""
]

for fpath in files_to_check:
    print(f"\nChecking: {fpath}")
    with open(fpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        for pat in secret_patterns:
            if re.search(pat, line):
                print(f"  Line {idx}: {line.strip()}")
