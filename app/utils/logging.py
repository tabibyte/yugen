import logging
from pathlib import Path

def setup_logging():
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger('yugen')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.FileHandler('logs/yugen.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger