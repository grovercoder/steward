import pickle
import os
import importlib.util
import inspect
import socket
import sys
import threading

from dotenv import load_dotenv

from steward.logger import logger

load_dotenv()

class StewardServer:
    def __init__(self, event_emitter=None):
        self._clients = {}

        self._validate_environment()        

    def _validate_environment(self):
        """
        Fail loudly if environment or configurations are not set properly
        """
        logger.info("Checking environment...")
        # Confirm we have the ENV variables we need
        messages = []
        for name in ["STEWARD_SOCKET_HOST", "STEWARD_SOCKET_PORT"]:
            if name not in os.environ or not os.getenv(name):
                messages.append(f"Missing ENV variables: {name}")
        
        if messages:
            for msg in messages:
                logger.error(msg)
            
            sys.exit(1)

        logger.info('Environment checks completed')





