#Logger = a diary that your program writes while running

"""Structured logging configuration for HealthRx AI."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "healthrx",
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Configure and return a structured logger instance.

    Args:
        name: Logger namespace identifier.
        level: Minimum log level for console output.
        log_to_file: Whether to persist logs to disk.

    Returns:
        Configured logging.Logger instance.

    Note:
        This function is idempotent — calling it multiple times with the
        same name returns the same logger without duplicate handlers.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console Handler ──────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ── File Handler ─────────────────────────────────────────────────
    if log_to_file:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"healthrx_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Module-level singleton for convenient import across the codebase.
logger: logging.Logger = setup_logger()