"""Logging utilities for the coding agent."""

import logging
import sys
from typing import Optional
from datetime import datetime


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Set level
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    else:
        logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for errors
    error_handler = logging.FileHandler('coding_agent_errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_rich_logging(level: str = "INFO") -> None:
    """Setup rich logging with colors and better formatting."""
    try:
        from rich.logging import RichHandler
        from rich.console import Console
        
        console = Console()
        
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)]
        )
    except ImportError:
        # Fallback to regular logging if rich is not available
        get_logger(__name__, level)


class SessionLogger:
    """Logger that maintains session context."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = get_logger(f"session_{session_id}")
        self.start_time = datetime.now()
    
    def log_intent(self, intent: str) -> None:
        """Log user intent."""
        self.logger.info(f"[INTENT] {intent}")
    
    def log_code_generation(self, file_path: str, operation: str) -> None:
        """Log code generation activity."""
        self.logger.info(f"[CODE] {operation} -> {file_path}")
    
    def log_execution(self, command: str, success: bool, duration: float) -> None:
        """Log code execution."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[EXEC] {command} - {status} ({duration:.2f}s)")
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log errors with context."""
        self.logger.error(f"[ERROR] {context}: {error}")
    
    def get_session_summary(self) -> dict:
        """Get session summary."""
        duration = datetime.now() - self.start_time
        return {
            "session_id": self.session_id,
            "duration": str(duration),
            "start_time": self.start_time.isoformat()
        }
