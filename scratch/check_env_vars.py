import os

print("=== ENVIRONMENT VARIABLE INSPECTION ===")
for k, v in os.environ.items():
    if any(term in k.upper() for term in ["GEMINI", "API", "KEY", "REAL", "RUN"]):
        val_str = v[:5] + "..." if len(v) > 5 else v
        print(f"  {k} = {val_str}")
