"""
Logging configuration for NEDAF.

Provides centralized logging with both console and rotating file handlers.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from ViewModel.config import LOGS_FILE


def setup_logging(level=logging.INFO, log_file=None):
    """
    Configure logging for NEDAF.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to config.LOGS_FILE)

    Returns:
        Configured logger instance
    """
    if log_file is None:
        log_file = LOGS_FILE

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("nedaf")
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler - INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler - DEBUG and above with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (use __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"nedaf.{name}")
