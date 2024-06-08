import socket
import pickle
import threading
from nanoid import generate
from abc import abstractmethod
from collections import deque
from dotenv import load_dotenv
import time

from steward.logger import get_logger, COLORS

load_dotenv()

class BaseClient:
    """
    Provide the basic structure for a Stweard client.

    Specific clients are expected to be based on this class.
    """

    def __init__(self, id=None, socket_host=None, socket_port=None):
        super().__init__()

        if not id:
            id = f'C:{generate(size=10)}'
        
        self.id = id
        self.logger = get_logger(name=self.id, console=True, file="client.log")
        self._client_socket = None
        self._running = False
        self._SOCKET_HOST = socket_host
        self._SOCKET_PORT = socket_port
        self._receiver = None
        self._listening = False

    def start(self):
        self.connect()
        self.listen()

    def stop(self):
        self.logger.info(f'stopping client: [{self.id}]...')
        self._listening.clear()
        self.logger.debug('...cleared listening flag')
        if self._receiver.is_alive():
            self.logger.debug('...receiver still active - waiting for shut down')
            self._receiver.join()
        self.logger.debug('... reception stopped')
        self.disconnect()
        self.logger.info('Client shutdown completed')

    def listen(self):
        self._start_receiver()

        try:
            while self._running:
                self.client_actions()

        except KeyboardInterrupt:
            self.stop()


    def connect(self, socket_host=None, socket_port=None):
        """
        connect to the Steward server
        """
        if socket_host:
            self._SOCKET_HOST = socket_host
        
        if socket_port:
            self._SOCKET_PORT = socket_port


        try:
            if not self._SOCKET_HOST or not self._SOCKET_PORT:
                self.logger.error('Socket Host or Port not specified')
                raise Exception('Socket Host or Port not specified')
            
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self._SOCKET_HOST, int(self._SOCKET_PORT))
            self.logger.info(f'Connecting to server {server_address}')
            self._client_socket.connect(server_address)
            self._running = True
            
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
        
    def disconnect(self):
        """
        disconnect from the steward server
        """
        if self._client_socket:
            try:
                self.logger.debug('disconnecting from server')
                self._running = False
                self._client_socket.close()
            
            except Exception as e:
                print(f'Disconnect error: {e}')
            finally:
                self._client_socket = None

    def _start_receiver(self):
        """
        start listening for messages from the server
        """
        self._receiver = threading.Thread(target=self._receive)
        self._receiver.daemon = True
        self._receiver.start()
        self._listening = threading.Event()
        self.logger.debug('Listening...')

    def _receive(self):
        while self._listening and self._listening.is_set():
            try:
                data = self._client_socket.recv(4096)
                if data:
                    message = pickle.loads(data)
                    self.logger.debug(f"data received: {message}")
                    self._handle_message(message)
  
            except Exception as e:
                self._logger.error(f'Reception Error: {e}')
                break
            finally:
                self._receiver.join()

        

    @abstractmethod
    def _handle_message(self, message):
        """
        Handle messages

        This method is expected to be replaced by the specific clients
        """
        pass

    def client_actions(self):
        """
        Perform any actions the client may need that are not covered by the socket connection
        """
        time.sleep(1)