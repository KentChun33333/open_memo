import logging
import sys
def get_logger(name):
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr
    )
    # Reduce noise
    logging.getLogger("mcp_agent").setLevel(logging.WARNING) 
    logger = logging.getLogger(name)
    return logger