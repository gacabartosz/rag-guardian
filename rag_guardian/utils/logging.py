"""Logging utilities for RAG Guardian.

This module provides a centralized logging configuration for the entire project.
All components should use get_logger(__name__) instead of print() statements.
"""

import logging
import os
import sys

# Default log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Global configuration
_loggers: dict[str, logging.Logger] = {}
_configured = False


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    """
    Get a configured logger for RAG Guardian.

    This function returns a logger configured with appropriate handlers
    and formatters. Loggers are cached to avoid duplicate configuration.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Optional logging level override. If not specified, uses
               RAG_GUARDIAN_LOG_LEVEL environment variable or defaults to INFO

    Returns:
        Configured logger instance

    Example:
        >>> from rag_guardian.utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting evaluation")
        >>> logger.error("Failed to load dataset")
    """
    global _configured

    # Return cached logger if exists
    if name in _loggers:
        return _loggers[name]

    # Create logger
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not _configured or not logger.handlers:
        # Determine log level
        if level is None:
            # Check environment variable
            env_level = os.getenv("RAG_GUARDIAN_LOG_LEVEL", "INFO").upper()
            level = getattr(logging, env_level, logging.INFO)

        logger.setLevel(level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        # Prevent propagation to root logger
        logger.propagate = False

        _configured = True

    # Cache logger
    _loggers[name] = logger

    return logger


def set_log_level(level: str) -> None:
    """
    Set log level for all RAG Guardian loggers.

    Args:
        level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> from rag_guardian.utils.logging import set_log_level
        >>> set_log_level("DEBUG")
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    for logger in _loggers.values():
        logger.setLevel(numeric_level)
        for handler in logger.handlers:
            handler.setLevel(numeric_level)


def disable_logging() -> None:
    """
    Disable all RAG Guardian logging output.

    Useful for testing or when running in quiet mode.

    Example:
        >>> from rag_guardian.utils.logging import disable_logging
        >>> disable_logging()
    """
    for logger in _loggers.values():
        logger.setLevel(logging.CRITICAL + 1)


def enable_file_logging(file_path: str, level: int | None = None) -> None:
    """
    Enable logging to file in addition to console.

    Args:
        file_path: Path to log file
        level: Optional log level for file handler

    Example:
        >>> from rag_guardian.utils.logging import enable_file_logging
        >>> enable_file_logging("rag_guardian.log")
    """
    if level is None:
        env_level = os.getenv("RAG_GUARDIAN_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(formatter)

    # Add to all existing loggers
    for logger in _loggers.values():
        logger.addHandler(file_handler)
