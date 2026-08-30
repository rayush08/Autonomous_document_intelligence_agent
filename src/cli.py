"""
Production Command Line Interface (CLI) for Autonomous Document Intelligence Agent.
"""

import sys
import os
import json
import argparse
from src.api import extract_document
from src.validator import validate_gold_records

def main():
    parser = argparse.ArgumentParser(description="Autonomous Document Intelligence Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: extract
    extract_parser = subparsers.add_parser("extract", help="Extract structured intelligence from a document")
    extract_parser.add_argument("--input", "-i", required=True, help="Path to input document file")
    extract_parser.add_argument("--output", "-o", help="Path to save output JSON result")
    extract_parser.add_argument("--domain", "-d", default="government_scheme", choices=["government_scheme", "opportunity"], help="Target extraction domain")
    extract_parser.add_argument("--real", action="store_true", help="Use real Gemini API (requires GEMINI_API_KEY env var)")
    extract_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose extraction logging")

    # Command: validate-gold
    validate_parser = subparsers.add_parser("validate-gold", help="Validate all 10 gold benchmark fixtures against schema")

    # Command: benchmark
    benchmark_parser = subparsers.add_parser("benchmark", help="Run system benchmark evaluation")
    benchmark_parser.add_argument("--mode", choices=["offline", "real"], default="offline", help="Benchmark execution mode")
    benchmark_parser.add_argument("--run-id", help="Optional run identifier for tracking")

    args = parser.parse_args()

    if args.command == "extract":
        use_mock = not args.real
        client = None

        if args.real:
            from src.llm.config import get_gemini_api_key
            from src.llm.gemini_client import GeminiLLMClient
            key = get_gemini_api_key()
            if not key:
                print("❌ Error: GEMINI_API_KEY environment variable is not set.")
                sys.exit(1)
            client = GeminiLLMClient.create_auto_discovered_client(api_key=key, verbose=args.verbose)

        result = extract_document(
            file_path=args.input,
            domain=args.domain,
            client=client,
            use_mock=use_mock,
            verbose=args.verbose
        )

        formatted_json = json.dumps(result, indent=2)

        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(formatted_json)
            print(f"✅ Extraction result saved to '{args.output}'.")
        else:
            print(formatted_json)

    elif args.command == "validate-gold":
        summary = validate_gold_records()
        print(f"\nSchema Validation Summary: {summary['valid_records']}/{summary['total_records']} Gold Records Valid.")

    elif args.command == "benchmark":
        from src.evaluation.run_evaluation import main as run_eval_main
        sys.argv = ["run_evaluation.py", f"--mode={args.mode}"]
        if args.run_id:
            sys.argv.append(f"--run-id={args.run_id}")
        run_eval_main()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
