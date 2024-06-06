import logging
import sys

# Define colors
COLORS = {
    'DEFAULT': '\033[0m',
    'INFO': '\033[94m',    # Blue
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m'    # Red
}

# Define formatter
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        color = COLORS.get(levelname, COLORS['DEFAULT'])
        record.levelname = f"{color}{levelname}{COLORS['DEFAULT']}"
        return super().format(record)

class FileFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record)

# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler with default formatter
file_handler = logging.FileHandler('logfile.log', mode="w" )
file_handler.setFormatter(FileFormatter('[%(asctime)s][%(levelname)s] %(message)s'))
logger.addHandler(file_handler)

# console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(ColoredFormatter(f'[%(asctime)s][%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

