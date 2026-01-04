"""
TCP JSON Client for communicating with firmware services
"""
import socket
import json
import time
from typing import Dict, Any, Optional


class TCPClient:
    """TCP client for JSON communication with firmware services."""

    def __init__(self, host: str, port: int, timeout: float = 5.0):
        """
        Initialize TCP client.

        Args:
            host: Service hostname/IP
            port: Service port number
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def connect(self):
        """Establish connection to service."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))

        # Server sends "Connection accepted\n" greeting, read and discard it
        greeting = b''
        while b'\n' not in greeting:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            greeting += chunk
        # Greeting received and discarded

    def disconnect(self):
        """Close connection to service."""
        if self.socket:
            self.socket.close()
            self.socket = None

    def send(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON request and receive response.

        Args:
            request: JSON request dictionary

        Returns:
            JSON response dictionary
        """
        # Convert to JSON and send
        request_str = json.dumps(request) + '\n'
        self.socket.sendall(request_str.encode('utf-8'))

        # Receive response
        time.sleep(0.15)
        response_data = b''
        while b'\n' not in response_data:
            chunk = self.socket.recv(4096)
            if not chunk:
                raise ConnectionError("Connection closed by server")
            response_data += chunk

        # Parse JSON response
        response_str = response_data.decode('utf-8').strip()
        return json.loads(response_str)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
