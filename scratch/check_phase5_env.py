import os

key_present = bool(os.getenv("GEMINI_API_KEY"))
flag_set = os.getenv("RUN_REAL_LLM_TESTS") == "1"

print("==========================================")
print("PHASE 5 PROCESS ENVIRONMENT CHECK")
print("==========================================")
print(f"GEMINI_API_KEY Present: {key_present}")
print(f"RUN_REAL_LLM_TESTS == '1': {flag_set}")
print("==========================================")
