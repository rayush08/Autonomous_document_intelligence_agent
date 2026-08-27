import os
import sys

def load_environment_config(env_file_path: str = None) -> dict:
    """Centralized environment configuration loader.
    
    Discovers and parses local .env files into os.environ without scattering load_dotenv() calls.
    Does NOT overwrite pre-existing system environment variables.
    """
    if env_file_path is not None:
        candidate_paths = [env_file_path]
    else:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        home_dir = os.path.expanduser("~")
        candidate_paths = [
            os.path.join(repo_root, ".env"),
            os.path.join(os.getcwd(), ".env"),
            os.path.join(home_dir, ".env"),
            os.path.join(home_dir, ".gemini", ".env"),
        ]

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and (k not in os.environ or not os.environ[k]):
                                os.environ[k] = v
            except Exception:
                pass


    api_key = os.environ.get("GEMINI_API_KEY", "")
    run_real = os.environ.get("RUN_REAL_LLM_TESTS", "")

    return {
        "has_api_key": bool(api_key and len(api_key) > 0),
        "run_real_flag": run_real == "1"
    }


def is_real_llm_mode_allowed(explicit_real_mode: bool = False) -> bool:
    """Determines whether real LLM API execution is authorized.
    
    Authorized if GEMINI_API_KEY is present AND (explicit_real_mode is True OR RUN_REAL_LLM_TESTS == '1').
    """
    config = load_environment_config()
    if not config["has_api_key"]:
        return False
    return explicit_real_mode or config["run_real_flag"]
