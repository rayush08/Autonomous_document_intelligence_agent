import os

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(repo_root, ".env")

print(f"Repo .env exists: {os.path.exists(env_file)}")
