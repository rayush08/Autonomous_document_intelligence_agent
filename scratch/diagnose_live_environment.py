import os
import sys

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.llm.config import load_environment_config

def run_diagnostic():

    load_environment_config()
    api_key = os.getenv("GEMINI_API_KEY")
    run_real = os.getenv("RUN_REAL_LLM_TESTS")
    
    # Discover .env file locations
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_root = os.path.join(repo_root, ".env")
    cwd_env = os.path.join(os.getcwd(), ".env")
    
    env_discovered = os.path.exists(env_root) or os.path.exists(cwd_env)

    
    dotenv_available = False
    try:
        import dotenv
        dotenv_available = True
    except ImportError:
        dotenv_available = False

    print("====================================")
    print("LIVE ENVIRONMENT DIAGNOSTIC")
    print("====================================")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print()
    print(f"GEMINI_API_KEY present: {bool(api_key)}")
    print(f"GEMINI_API_KEY non-empty: {len(api_key or '') > 0}")
    print()
    print(f"RUN_REAL_LLM_TESTS present: {bool(run_real)}")
    print(f"RUN_REAL_LLM_TESTS enabled: {run_real == '1'}")
    print()
    print(f"`.env` file discovered: {env_discovered}")
    print(f"dotenv available: {dotenv_available}")
    print("====================================")

if __name__ == "__main__":
    run_diagnostic()
