import logging
import sys
from typing import Optional

# Standard format
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
DATE_FORMAT = '%H:%M:%S'

def setup_logging(level=logging.INFO):
    """
    Configures the root logger. 
    Should be called ONCE by the Orchestrator entry point.
    """
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        stream=sys.stderr
    )
    # Reduce noise from external libraries
    logging.getLogger("mcp_agent").setLevel(logging.WARNING) 
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Factory for getting a named logger.
    Ensures consistent naming convention.
    """
    return logging.getLogger(name)
