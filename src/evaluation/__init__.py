"""
Phase 3 Evaluation Engine & Benchmark Package.
"""
from src.evaluation.evaluator import EvaluationEngine
from src.evaluation.metrics import compute_metrics
from src.evaluation.comparison import compare_field, compare_values
from src.evaluation.reporting import format_markdown_report, save_reports

__all__ = [
    "EvaluationEngine",
    "compute_metrics",
    "compare_field",
    "compare_values",
    "format_markdown_report",
    "save_reports"
]

