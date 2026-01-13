import logging
import sys
import io

def setup_logger(name="telegram_stories_bot"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console handler with UTF-8 support
        # We wrap sys.stdout to handle potential encoding issues in Windows console
        try:
            ch = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
        except:
            ch = logging.StreamHandler(sys.stdout)
            
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    
    return logger
