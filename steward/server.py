import pickle
import os
import importlib.util
import inspect
import select
import socket
import sys
import threading
import time

from dotenv import load_dotenv

from steward.logger import get_logger
from steward.event import StewardEvent

# load the environment variables
load_dotenv()

class StewardServer:
    """
    The Steward Server
    """
    def __init__(self, event_emitter=None, logLevel="INFO"):
        self._server_socket = None
        self._running = False
        self._clients = {}
        self.logger = get_logger(name="Steward", level=logLevel, console=True, file="logs/server.log")
    
    def _validate_environment(self):
        """
        Fail loudly if environment or configurations are not set properly
        """
        self.logger.info("Checking environment...")
        # Confirm we have the ENV variables we need
        success = True
        for name in ["STEWARD_SOCKET_HOST", "STEWARD_SOCKET_PORT"]:
            if name not in os.environ or not os.getenv(name):
                self.logger.error(f'Missing ENV variable: {name}')
                success = False
        
        if not success:
            self.logger.error("Invalid environment.  Exiting")
            sys.exit(1)

        self.logger.info('Environment checks completed')

    def start(self):
        """
        Start the Steward
        """
        # included logic here to setup, configure, and launch the system
        # including scanning for plugins, establishing connections, etc.

        # confirm the environment is configured
        self._validate_environment()    

        # Start the steward socket server
        self._start_socket_server()

    def stop(self):
        """
        Stop the Steward
        """
        self.logger.warn("Stopping Socket Server")
        for client_address, conn in list(self._clients.items()):
            try:
                self.logger.info(f" - notifying client: {client_address}")
                msg = StewardEvent(name="STEWARD_STOPPING")
                serialized = msg.serialize()
                conn.sendall(serialized)

                time.sleep(0.5)

                if self._is_socket_connected(conn):
                    conn.close()                
                
                del self._clients[client_address]

            except Exception as e:
                print(e)
                self.logger.error(f"ERROR Disconnecting {client_address}")

        self._server_socket.close()
        self._running = False
        # sys.exit(0)

    def _is_socket_connected(self, conn):
        try:
            # Use select to check for socket status
            ready_to_read, ready_to_write, in_error = select.select([conn], [conn], [conn], 0)
            if in_error:
                return False
            return True
        except Exception as e:
            return False
        
    def _start_socket_server(self):
        """
        Start the socket server
        """
        host = os.getenv("STEWARD_SOCKET_HOST")
        port = int(os.getenv("STEWARD_SOCKET_PORT"))
        server_address = (host, port)

        # indicate the server is running
        self._running = True

        # Create a socket
        self.logger.info("Starting socket service")
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(server_address)
        self._server_socket.listen(5)
        self.logger.info("Listening for connections")

        while self._running:
            try:
                # Accept a connection
                connection, client_address = self._server_socket.accept()
                # create a new thread for each client connection
                client_handler = threading.Thread(target=self._handle_client, args=(connection, client_address))
                client_handler.start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                if self._running:
                    print(f"Error accepting connections: {e}")
                 
    def _handle_client(self, connection, client_address):
        """
        Manage a client connection
        """
        # remember the client connection
        self._clients[client_address] = connection
        self.logger.info(f"client connection: {client_address}")
        
        data = "welcome"
        message = pickle.dumps(data)
        connection.sendall(message)
        self.logger.debug('wecomone sent')

        # respond to incoming messages from the client
        try:
            while True:
                data = connection.recv(4096)

                if data:
                    message = pickle.loads(data)
                    self.logger.debug(f"[{client_address}]: {message}")

        except Exception as e:
            self.logger.error(f"client error [{client_address}] {e}")
        finally:
            if self._is_socket_connected(connection):
                # close the connection
                connection.close()

            # remove the client from the clients list
            if client_address in self._clients:
                del self._clients[client_address]


