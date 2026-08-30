import os

api_key = os.environ.get("GEMINI_API_KEY")
run_real = os.environ.get("RUN_REAL_LLM_TESTS")

has_key = bool(api_key and len(api_key) > 5)
is_flag_set = run_real == "1"

print("==========================================")
print("ENVIRONMENT DIAGNOSTIC CHECK")
print("==========================================")
print(f"GEMINI_API_KEY Present: {has_key}")
print(f"RUN_REAL_LLM_TESTS == '1': {is_flag_set}")
print("==========================================")
