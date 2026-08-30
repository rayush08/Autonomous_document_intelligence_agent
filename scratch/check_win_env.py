import os
import subprocess

def check_win_registry():
    cmd = 'powershell -Command "[Environment]::GetEnvironmentVariable(\'GEMINI_API_KEY\', \'User\')"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    user_key = res.stdout.strip()
    
    cmd_machine = 'powershell -Command "[Environment]::GetEnvironmentVariable(\'GEMINI_API_KEY\', \'Machine\')"'
    res_m = subprocess.run(cmd_machine, shell=True, capture_output=True, text=True)
    machine_key = res_m.stdout.strip()

    cmd_flag = 'powershell -Command "[Environment]::GetEnvironmentVariable(\'RUN_REAL_LLM_TESTS\', \'User\')"'
    res_f = subprocess.run(cmd_flag, shell=True, capture_output=True, text=True)
    user_flag = res_f.stdout.strip()

    print("=== SAFE WINDOWS ENVIRONMENT REGISTRY CHECK ===")
    print(f"User Registry Key Present: {bool(user_key and len(user_key) > 5)}")
    print(f"Machine Registry Key Present: {bool(machine_key and len(machine_key) > 5)}")
    print(f"User Registry Flag Present: {user_flag == '1'}")

if __name__ == "__main__":
    check_win_registry()
