import logging
import sys

# Define colors
COLORS = {
    'DEFAULT': '\033[0m',
    'BLACK': '\033[30m',
    'BLUE': '\033[34m',
    'BRIGHT_BLACK': '\033[90m',
    'BRIGHT_BLUE': '\033[94m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_MAGENTA': '\033[95m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_WHITE': '\033[97m',
    'BRIGHT_YELLOW': '\033[93m',
    'CYAN': '\033[36m',
    'GREEN': '\033[32m',
    'MAGENTA': '\033[35m',
    'RED': '\033[31m',
    'WHITE': '\033[37m',
    'YELLOW': '\033[33m',
}
COLORS['INFO'] = COLORS['BRIGHT_BLUE']
COLORS['WARNING'] = COLORS['BRIGHT_YELLOW']
COLORS['WARN'] = COLORS['BRIGHT_YELLOW']
COLORS['ERROR'] = COLORS['BRIGHT_RED']

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

