import copy
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from nanoid import generate

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
    'ORANGE': '\033[38;5;208m',
    'RED': '\033[31m',
    'WHITE': '\033[37m',
    'YELLOW': '\033[33m',
}
COLORS['INFO'] = COLORS['BRIGHT_BLUE']
COLORS['WARNING'] = COLORS['BRIGHT_YELLOW']
COLORS['WARN'] = COLORS['BRIGHT_YELLOW']
COLORS['ERROR'] = COLORS['BRIGHT_RED']
COLORS['DEBUG'] = COLORS['ORANGE']


# Define formatter
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        clone = copy.deepcopy(record)
        levelname = clone.levelname
        color = COLORS.get(levelname, COLORS['DEFAULT'])
        clone.levelname = f"{color}{levelname}{COLORS['DEFAULT']}"
        return super().format(clone)

class FileFormatter(logging.Formatter):
    def format(self, record):
        clone = copy.deepcopy(record)
        return super().format(clone)

def get_logger(name=None, level="INFO", console=False, file=None, mode="a"):
    """
    Generate a logging object
    """
    if not name:
        # set the name to a unique identifier 
        name = f"L{generate(size=8)}"

    output = logging.getLogger(name)
    output.setLevel(level)
    
    if console:
        ch = logging.StreamHandler(sys.stdout)
        # ch.setLevel(level)
        ch.setFormatter(ColoredFormatter(f'[%(asctime)s][%(levelname)s] %(message)s'))
        output.addHandler(ch)
    
    if file:
        if not os.path.exists(file):
            dirname = os.path.dirname(file)
            os.makedirs(dirname, exist_ok=True)

        # setting the maxBytes to 10MB
        fh = RotatingFileHandler(file, maxBytes=10 * 1024 * 1024, backupCount=10, mode=mode)
        # fh.setLevel(level)
        fh.setFormatter(FileFormatter('[%(asctime)s][%(levelname)s] %(message)s'))
        output.addHandler(fh)
    
    return output


