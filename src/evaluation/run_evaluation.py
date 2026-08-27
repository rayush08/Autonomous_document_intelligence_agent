import os
import sys
import argparse
from src.evaluation.evaluator import EvaluationEngine
from src.evaluation.reporting import save_reports
from src.llm.gemini_client import GeminiLLMClient
from src.llm.llm_extractor import LLMExtractor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS_DIR = os.path.join(BASE_DIR, "evaluation", "results")


def main():
    parser = argparse.ArgumentParser(description="Run Phase 3 Evaluation Benchmark Engine")
    parser.add_argument("--mode", choices=["offline", "real"], default="offline", help="Evaluation mode: 'offline' baseline vs 'real' Gemini LLM pipeline")
    parser.add_argument("--run-id", type=str, default=None, help="Optional run iteration ID (e.g. 1, 2, 3, phase4_1) for multi-run benchmarks")

    args = parser.parse_args()

    mode = args.mode
    run_id = args.run_id
    run_str = f" RUN #{run_id}" if run_id else ""
    print("==========================================================")
    print(f"   AUTONOMOUS DOCUMENT INTELLIGENCE AGENT - PHASE 3")
    print(f"   BENCHMARK EVALUATION ENGINE ({mode.upper()} MODE{run_str})")
    print("==========================================================")

    extractor = None

    if mode == "real":
        from src.llm.config import load_environment_config, is_real_llm_mode_allowed
        load_environment_config()
        api_key = os.environ.get("GEMINI_API_KEY")

        if not is_real_llm_mode_allowed(explicit_real_mode=True):
            print("\n⚠️ REAL LLM EVALUATION SKIPPED: GEMINI_API_KEY environment variable is missing.")
            print("   -> Offline benchmark results remain preserved and untainted.")
            print("   -> Set $env:GEMINI_API_KEY or configure .env to execute real Gemini evaluation.\n")
            sys.exit(0)

        print("🔍 Performing real Gemini client discovery and smoke testing...")
        client = GeminiLLMClient.create_auto_discovered_client(api_key=api_key, verbose=True)
        extractor = LLMExtractor(llm_client=client)


    engine = EvaluationEngine(extractor=extractor)
    metrics = engine.run_benchmark()

    overall = metrics.get("overall", {})
    print(f"\n✅ Benchmark Execution Completed across {overall.get('total_documents_evaluated', 0)} documents!")
    print(f"   -> Schema Validity Rate:           {overall.get('schema_validity_rate', 0.0) * 100:.1f}%")
    print(f"   -> Field Extraction Accuracy:       {overall.get('field_extraction_accuracy', 0.0) * 100:.1f}%")
    print(f"   -> Verification Status Accuracy:   {overall.get('verification_status_accuracy', 0.0) * 100:.1f}%")
    print(f"   -> Missing Info Accuracy:          {overall.get('missing_information_accuracy', 0.0) * 100:.1f}%")
    print(f"   -> Hallucination / Unsupported:    {overall.get('hallucination_rate', 0.0) * 100:.1f}%\n")

    save_reports(metrics, RESULTS_DIR, mode=mode, run_id=run_id)


if __name__ == "__main__":
    main()


