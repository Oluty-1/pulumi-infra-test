import logging
from typing import Optional

def setup_logger(name: str, level: Optional[str] = "INFO") -> logging.Logger:
    """Configure logging for the infrastructure deployment"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
