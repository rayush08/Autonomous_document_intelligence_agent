import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from src.llm.config import load_environment_config, is_real_llm_mode_allowed


class TestEnvironmentLoadingAndGating(unittest.TestCase):
    """Regression test suite for environment loading, key propagation, and real-mode gating."""

    def setUp(self):
        self.original_env = os.environ.copy()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_A_environment_variable_detection(self):
        """Test A: Mocked GEMINI_API_KEY is detected correctly."""
        os.environ["GEMINI_API_KEY"] = "mock_secret_key_12345"
        config = load_environment_config()
        self.assertTrue(config["has_api_key"])

    def test_B_missing_credential_handling(self):
        """Test B: Missing key is handled cleanly without raising unhandled exceptions or exposing secrets."""
        with unittest.mock.patch("src.llm.config.load_environment_config", return_value={"has_api_key": False, "run_real_flag": False}):
            with unittest.mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
                config = load_environment_config(env_file_path=os.path.join(self.temp_dir, "non_existent.env"))
                self.assertFalse(config["has_api_key"])
                self.assertFalse(is_real_llm_mode_allowed(explicit_real_mode=True))

    def test_C_real_mode_gating(self):
        """Test C: Real-mode gating policy distinguishes offline vs real mode with key vs missing key."""
        with unittest.mock.patch.dict(os.environ, {"GEMINI_API_KEY": "", "RUN_REAL_LLM_TESTS": "0"}):
            with unittest.mock.patch("src.llm.config.load_environment_config", return_value={"has_api_key": False, "run_real_flag": False}):
                self.assertFalse(is_real_llm_mode_allowed(explicit_real_mode=True))

        os.environ["GEMINI_API_KEY"] = "mock_secret_key_12345"
        self.assertTrue(is_real_llm_mode_allowed(explicit_real_mode=True))


    def test_D_subprocess_environment_propagation(self):
        """Test D: Environment variables set in python os.environ propagate to child sub-processes."""
        import subprocess
        os.environ["GEMINI_API_KEY"] = "mock_key_for_subproc"
        code = "import os; print(bool(os.environ.get('GEMINI_API_KEY')))"
        res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertIn("True", res.stdout)

    def test_E_env_development_loading(self):
        """Test E: Temporary .env file parsing loads keys into os.environ."""
        env_path = os.path.join(self.temp_dir, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("# Temporary test env\nGEMINI_API_KEY=file_loaded_key_999\nRUN_REAL_LLM_TESTS=1\n")

        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

        config = load_environment_config(env_file_path=env_path)
        self.assertTrue(config["has_api_key"])
        self.assertEqual(os.environ.get("GEMINI_API_KEY"), "file_loaded_key_999")


if __name__ == "__main__":
    unittest.main()
