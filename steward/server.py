import pickle
import os
import importlib.util
import inspect
import select
import signal
import socket
import sys
import threading
import time

from dotenv import load_dotenv

from steward.logger import get_logger
from steward.event import StewardEvent

# load the environment variables
load_dotenv()


class ClientConnection:
    def __init__(self, connection=None, address=None, id=None, details=None, thread=None, logger=None):
        self.connection = connection
        self.address = address
        self.id = id
        self.details = details
        self.thread = thread
        self._registered = False
        self.logger = logger
    
    def log(self, level="INFO", message=None):
        if self.logger and message:
            logmethod = self.logger.log_methods.get(str(level).upper(), self.logger.info)
            logmethod(msg=message)

    def register(self, info=None):
        print('------ register ------')
        if info:
            self.id = info.get('id', None)
            self.details = info

            self._registered = True
            self.log(message=f'client {self.id} [{self.address}] registered')

    def is_connected(self):
        try:
            ready_to_read, ready_to_write, in_error = select.select([self.connection], [self.connection], [self.connection], 0)
            return not in_error
        except Exception as e:
            return False
        
    def send_message(self, message):
        if self.is_connected():
            if isinstance(message, StewardEvent):
                self.connection.sendall(message.serialize())
            else:
                serialized = pickle.dumps(message)
                self.connection.sendall(serialized)

    def disconnect(self):
        try:
            self.log(level='info', message=f'disconnecting {self.id} [{self.address}]')

            msg = StewardEvent(name="CLIENT_DISCONNECT", payload={"id": self.id})
            self.send_message(msg)
            
            time.sleep(0.5)

            if self.is_connected():
                self.connection.close()

        except Exception as e:
            self.log(level='error', message=f"ERROR Disconnecting {self.id} [{self.address}]: {e}")


class StewardServer:
    """
    The Steward Server
    """
    def __init__(self, event_emitter=None, logLevel="INFO"):
        self._server_socket = None
        self._running = False
        self._clients = []
        self._client_threads = []
        self.logger = get_logger(name="Steward", level=logLevel, console=True, file="logs/server.log")
        
        # catch and handle the interrupt signal
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.logger.warn('Interrupt signal received')
        self.stop()

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
        self._running = False

        for client in list(self._clients):
            try:
                self.logger.info(f" - notifying client: {client.id}")
                msg = StewardEvent(name="STEWARD_STOPPING")
                client.send_message(msg)
                # serialized = msg.serialize()
                # client["connection"].sendall(serialized)

                time.sleep(0.5)

                if client.is_connected():
                    client.disconnect()
                    # client["connection"].close()                
                
                self._clients.remove(client)

            except Exception as e:
                print("ERROR: ")
                print(e)
                self.logger.error(f"ERROR Disconnecting {client_address}")
        
        # Close the server socket
        if self._server_socket:
            self._server_socket.close()

        # Join all client threads
        for thread in self._client_threads:
            thread.join()

        self.logger.info("Steward server stopped")
        sys.exit(0)

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
        self._server_socket.settimeout(1)
        self.logger.info("Listening for connections")

        while self._running:
            try:
                # Accept a connection
                connection, client_address = self._server_socket.accept()
                # create a new thread for each client connection
                client_handler = threading.Thread(target=self._handle_client, args=(connection, client_address))

                client_connection = ClientConnection(
                    address=client_address,
                    connection=connection,
                    thread=client_handler,
                    logger=self.logger
                    )
                
                print('--- client_connection ---')
                print(client_connection)

                self._clients.append(client_connection)
                # self._client_threads.append(client_handler)
                client_handler.start()

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                if self._running:
                    self.logger.error(f"Error accepting connection: {e}")
                 
    def _handle_client(self, connection, client_address):
        """
        Manage a client connection
        """
        print(self._clients)
        client_info = next((client for client in self._clients if client.address == client_address), None)
        print('-----')
        print(f'client_info: , {client_info}')
        if not client_info:
            return
        
        # # remember the client connection
        # self._clients[client_address] = {
        #     "address": client_address,
        #     "connection": connection,
        #     "details": None
        # }

        # self.logger.info(f"client connection: {client_address}")
        
        # respond to incoming messages from the client
        try:
            while self._running:
                data = connection.recv(4096)

                if data:
                    message = pickle.loads(data)
                    self.logger.debug(f"[{client_address}]: {message}")

                    if isinstance(message, StewardEvent):

                        self.logger.info(f'EVENT: [{message.name}] {message.payload}')

                        if message.name == 'CLIENT_DISCONNECT':
                            del self._clients[client_address]
                            self.logger.info(f"Client Disconnected: {client_address}")
                            break

                        if message.name == 'CLIENT_REGISTER':
                            client_info.register(message.payload)
                            # self._clients[client_address]['details'] = message.payload
                            # self.logger.info(f'client {self._clients[client_address]} connected')

        except Exception as e:
            self.logger.error(f"client error [{client_address}] {e}")
        finally:
            if self._is_socket_connected(connection):
                # close the connection
                connection.close()

            # remove the client from the clients list
            if client_address in self._clients:
                del self._clients[client_address]


