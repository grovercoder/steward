import pickle
import os
import importlib.util
import inspect
import socket
import sys
import threading

from dotenv import load_dotenv

from steward.logger import get_logger

# load the environment variables
load_dotenv()
logger = get_logger(name="Steward", console=True, file="logfile.log")
class StewardServer:
    """
    The Steward Server
    """
    def __init__(self, event_emitter=None):
        self._server_socket = None
        self._running = False
        self._clients = {}


    def _validate_environment(self):
        """
        Fail loudly if environment or configurations are not set properly
        """
        logger.info("Checking environment...")
        # Confirm we have the ENV variables we need
        success = True
        for name in ["STEWARD_SOCKET_HOST", "STEWARD_SOCKET_PORT"]:
            if name not in os.environ or not os.getenv(name):
                logger.error(f'Missing ENV variable: {name}')
                success = False
        
        if not success:
            logger.error("Invalid environment.  Exiting")
            sys.exit(1)

        logger.info('Environment checks completed')

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
        logger.warn("Stopping Socket Server")
        for client_address, conn in self._clients.items():
            try:
                logger.info(f"  - disconnecting client: {client_address}")
                conn.close()
            except Exception as e:
                logger.error("    ERROR Disconnecting {client_address}")

        self._server_socket.close()
        self._running = False
        # sys.exit(0)

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
        logger.info("Starting socket service")
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(server_address)
        self._server_socket.listen(5)
        logger.info("Listening for connections")

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
        logger.info(f"client connection: {client_address}")

        # respond to incoming messages from the client
        try:
            while True:
                data = connection.recv(4096)
                if not data:
                    break

                message = pickle.loads(data)

                logger.log(f"[{client_address}]: message")

        except Exception as e:
            logger.error(f"client error [{client_address}] {e}")
        finally:
            # close the connection
            connection.close()

            # remove the client from the clients list
            del self._clients[client_address]


