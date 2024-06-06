import sys
import pytest
from unittest.mock import patch, MagicMock
from steward.server import StewardServer

@pytest.fixture
def mock_logger(monkeypatch):
    mock_logger = MagicMock()
    monkeypatch.setattr('steward.server.logger', mock_logger)
    return mock_logger

@pytest.fixture
def mock_socket(monkeypatch):
    mock_socket = MagicMock()
    monkeypatch.setattr('socket.socket', MagicMock(return_value=mock_socket))
    return mock_socket

@pytest.fixture
def mock_thread(monkeypatch):
    mock_thread = MagicMock()
    monkeypatch.setattr('threading.Thread', mock_thread)
    return mock_thread

def test_validate_environment_success(monkeypatch, mock_logger):
    """
    Test the _validate_environment() method with a configured environment
    """
    # Set the environment variables
    monkeypatch.setenv("STEWARD_SOCKET_HOST", "localhost")
    monkeypatch.setenv("STEWARD_SOCKET_PORT", "8080")
    
    server = StewardServer()
    server._validate_environment()

    # Check that the logger.info method was called with the expected messages
    mock_logger.info.assert_any_call("Checking environment...")
    mock_logger.info.assert_any_call("Environment checks completed")

@patch('sys.exit')
def test_validate_environment_failure(mock_exit, monkeypatch, mock_logger):
    """
    Test the _validate_environment() method with a misconfigured environment
    """
    # Clear the environment variables
    monkeypatch.delenv("STEWARD_SOCKET_HOST", raising=False)
    monkeypatch.delenv("STEWARD_SOCKET_PORT", raising=False)
    
    server = StewardServer()
    server._validate_environment()

    # Check that the logger.error method was called with the expected message
    mock_logger.error.assert_any_call("Missing ENV variable: STEWARD_SOCKET_HOST")
    mock_logger.error.assert_any_call("Missing ENV variable: STEWARD_SOCKET_PORT")

    # Check that sys.exit(1) was called
    mock_exit.assert_called_once_with(1)

def test_start_success(mock_logger, mock_socket, mock_thread, monkeypatch):
    """
    confirm the .start() method succeeds
    """
    # Set the environment variables
    monkeypatch.setenv("STEWARD_SOCKET_HOST", "localhost")
    monkeypatch.setenv("STEWARD_SOCKET_PORT", "8080")
    
    server = StewardServer()
    server.start()

    # Validate socket server start logs
    mock_logger.info.assert_any_call("Starting socket service")
    mock_logger.info.assert_any_call("Listening for connections")

    # Ensure the socket methods are called correctly
    mock_socket.bind.assert_called_once_with(('localhost', 8080))
    mock_socket.listen.assert_called_once_with(5)

def test_stop(mock_logger, mock_socket, monkeypatch):
    """
    test the .stop() method
    """
    server = StewardServer()
    
    # Simulate a client connection
    mock_conn = MagicMock()
    client_address = ('127.0.0.1', 5000)
    server._clients[client_address] = mock_conn
    
    # Mock the server socket
    server._server_socket = mock_socket

    server.stop()

    # Check the logs
    mock_logger.warn.assert_called_once_with("Stopping Socket Server")
    mock_logger.info.assert_called_with(f"  - disconnecting client: {client_address}")

    # Ensure the connection close method is called
    mock_conn.close.assert_called_once()

    # Ensure the server socket close method is called
    mock_socket.close.assert_called_once()

    # Ensure the server is marked as not running
    assert not server._running