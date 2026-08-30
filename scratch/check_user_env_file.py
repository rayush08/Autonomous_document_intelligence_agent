import os

user_env = os.path.expanduser("~/.env")
print("Checking path:", user_env)

if os.path.exists(user_env):
    print("File exists!")
    with open(user_env, "r", encoding="utf-8") as f:
        lines = f.readlines()
    keys = [line.split("=")[0].strip() for line in lines if "=" in line]
    print("Found keys in ~/.env:", keys)
else:
    print("File ~/.env does not exist.")
