"""
Structured Observability and Logging Module for Autonomous Document Intelligence Agent.
Provides production-grade logging with contextual metadata (request IDs, document IDs, timing, and errors).
"""

import os
import sys
import logging
import json
import time

class JsonFormatter(logging.Formatter):
    """Formats log records as structured JSON for production log aggregators."""
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if hasattr(record, "doc_id"):
            log_obj["doc_id"] = record.doc_id
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "latency_ms"):
            log_obj["latency_ms"] = record.latency_ms
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name="document_intelligence", log_file=None, json_format=False, level=logging.INFO):
    """
    Retrieves or configures a logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        if json_format:
            console_handler.setFormatter(JsonFormatter())
        else:
            fmt = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            console_handler.setFormatter(fmt)

        logger.addHandler(console_handler)

        if log_file:
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(JsonFormatter() if json_format else fmt)
            logger.addHandler(file_handler)

    return logger

logger = get_logger()
