import os

gemini_keys = [k for k in os.environ.keys() if "GEMINI" in k.upper() or "API_KEY" in k.upper() or "GOOGLE" in k.upper()]
print("Matching env keys:", gemini_keys)
