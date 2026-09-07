import logging
import os
import sys

def get_logger(name: str) -> logging.Logger:
    """Configure and return a standard logger for the application."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Create console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Create file handler for the specific agent
        os.makedirs("logs", exist_ok=True)
        agent_name = name.split('.')[-1] if '.' in name else name
        fh = logging.FileHandler(f"logs/{agent_name}.log")
        fh.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to handlers
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        
    return logger
