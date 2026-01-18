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
        self._buffer = b''  # Buffer for handling partial/multiple messages

    def connect(self):
        """Establish connection to service."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.connect((self.host, self.port))
        self._buffer = b''  # Clear buffer on connect

        # Server sends "Connection accepted\n" greeting, read and discard it
        greeting = b''
        while b'\n' not in greeting:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            greeting += chunk
        # Check if greeting contains more data after the newline
        if b'\n' in greeting:
            idx = greeting.index(b'\n') + 1
            self._buffer = greeting[idx:]  # Save any extra data

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

        # Receive response (use buffered read)
        time.sleep(0.15)
        return self._recv_line()

    def send_async(self, request: Dict[str, Any]) -> None:
        """
        Send JSON request without waiting for response.

        Use recv() to capture async push messages afterwards.

        Args:
            request: JSON request dictionary
        """
        request_str = json.dumps(request) + '\n'
        self.socket.sendall(request_str.encode('utf-8'))

    def _recv_line(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Internal method to receive a single JSON line with proper buffering.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            JSON response dictionary

        Raises:
            ConnectionError: If connection closed
            socket.timeout: If timeout occurs
        """
        old_timeout = self.socket.gettimeout()
        if timeout is not None:
            self.socket.settimeout(timeout)

        try:
            # Check if we already have a complete line in the buffer
            while b'\n' not in self._buffer:
                chunk = self.socket.recv(4096)
                if not chunk:
                    raise ConnectionError("Connection closed by server")
                self._buffer += chunk

            # Extract the first line from the buffer
            idx = self._buffer.index(b'\n')
            line = self._buffer[:idx]
            self._buffer = self._buffer[idx + 1:]  # Keep remainder for next call

            # Parse JSON response
            response_str = line.decode('utf-8').strip()
            if not response_str:
                raise ValueError("Empty response line")
            return json.loads(response_str)
        finally:
            if timeout is not None:
                self.socket.settimeout(old_timeout)

    def recv(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Receive JSON message without sending.

        Args:
            timeout: Optional timeout in seconds (overrides socket timeout)

        Returns:
            JSON response dictionary, or None if timeout/no data
        """
        try:
            return self._recv_line(timeout=timeout)
        except socket.timeout:
            return None
        except (ConnectionError, ValueError):
            return None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
