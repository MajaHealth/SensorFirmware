#!/usr/bin/env python3
"""
Mock SPI_DEV_servise - Simulates ECG (ADS1293) and ICG (MAX30009) sensor services.

ECG Port: 1293
ICG Port: 30009

This mock service reads sample data from sample_data.txt and returns it when requested.

Usage:
    python3 mock_spi_dev_service.py [--sample-data /path/to/sample_data.txt]

Note: Make sure the real SPI_DEV_servise is not running, or ports will conflict.
      Stop it with: sudo systemctl stop spi_dev_service (or kill the process)
"""

import socket
import threading
import json
import time
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# Ports
ECG_PORT = 1293
ICG_PORT = 30009

# Sync mark magic number
SYNC_MARK_MAGIC_NUM = -99999
ICG_SYNC_MARK_MAGIC_NUM = -999990000


def check_port_available(port: int) -> bool:
    """Check if a port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Port is available if connection fails
    except:
        return True


class MockDataLoader:
    """Loads and manages mock data from sample_data.txt"""

    def __init__(self, data_file: str = None):
        self.ecg_data: List[List[int]] = []
        self.icg_data: List[List[int]] = []
        self.ecg_index = 0
        self.icg_index = 0
        self._load_data(data_file)

    def _load_data(self, data_file: str):
        """Parse sample_data.txt and load ECG and ICG data"""
        # Try multiple locations for sample_data.txt
        possible_paths = []

        if data_file:
            possible_paths.append(data_file)

        # Same directory as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(script_dir, "sample_data.txt"))

        # Current working directory
        possible_paths.append(os.path.join(os.getcwd(), "sample_data.txt"))

        # Home directory
        possible_paths.append(os.path.expanduser("~/sample_data.txt"))

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            print(f"Warning: sample_data.txt not found in any of these locations:")
            for path in possible_paths:
                print(f"  - {path}")
            print("Using built-in default data instead.")
            self._use_default_data()
            return

        print(f"Loading sample data from: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Find ECG data section (after "Mock ecg data")
            ecg_start = content.find('[', content.find('Mock ecg data'))
            ecg_end = content.find(']', ecg_start)
            # Find matching closing bracket
            bracket_count = 1
            pos = ecg_start + 1
            while bracket_count > 0 and pos < len(content):
                if content[pos] == '[':
                    bracket_count += 1
                elif content[pos] == ']':
                    bracket_count -= 1
                pos += 1
            ecg_end = pos
            ecg_json = content[ecg_start:ecg_end]
            self.ecg_data = json.loads(ecg_json)

            # Find ICG data section (after "Mock ICG data")
            icg_start = content.find('[', content.find('Mock ICG data'))
            bracket_count = 1
            pos = icg_start + 1
            while bracket_count > 0 and pos < len(content):
                if content[pos] == '[':
                    bracket_count += 1
                elif content[pos] == ']':
                    bracket_count -= 1
                pos += 1
            icg_end = pos
            icg_json = content[icg_start:icg_end]
            self.icg_data = json.loads(icg_json)

            print(f"Loaded {len(self.ecg_data)} ECG samples and {len(self.icg_data)} ICG samples")

        except Exception as e:
            print(f"Error loading sample data: {e}")
            self._use_default_data()

    def _use_default_data(self):
        """Use built-in default data when sample_data.txt is not available"""
        print("Using built-in default data (100 samples each)")
        self.ecg_data = [[4124978, 6327300, 4094084] for _ in range(100)]
        self.icg_data = [[5407359, 5629832, -1566996, -161610, 1] for _ in range(100)]

    def get_ecg_samples(self, count: int) -> List[List[int]]:
        """Get a batch of ECG samples, cycling through data"""
        samples = []
        for _ in range(count):
            samples.append(self.ecg_data[self.ecg_index].copy())
            self.ecg_index = (self.ecg_index + 1) % len(self.ecg_data)
        return samples

    def get_icg_samples(self, count: int) -> List[List[int]]:
        """Get a batch of ICG samples, cycling through data"""
        samples = []
        for _ in range(count):
            samples.append(self.icg_data[self.icg_index].copy())
            self.icg_index = (self.icg_index + 1) % len(self.icg_data)
        return samples

    def reset_indices(self):
        """Reset data indices to start"""
        self.ecg_index = 0
        self.icg_index = 0


class ECGMockHandler:
    """Handles ECG (ADS1293) mock commands"""

    def __init__(self, data_loader: MockDataLoader):
        self.data_loader = data_loader
        self.settings = {
            "power_enable": False,
            "enable_conversion": False,
            "R2_rate": 4,
            "R3_rate": 16
        }
        self.sync_num = 0
        self.last_sync_time = time.time()
        self.data_buffer: List[List[int]] = []
        self.running = False
        self.data_thread: Optional[threading.Thread] = None

    def start_data_collection(self):
        """Start background data collection thread"""
        if self.running:
            return
        self.running = True
        self.data_thread = threading.Thread(target=self._collect_data, daemon=True)
        self.data_thread.start()

    def stop_data_collection(self):
        """Stop background data collection"""
        self.running = False
        if self.data_thread:
            self.data_thread.join(timeout=1.0)
            self.data_thread = None

    def _collect_data(self):
        """Background thread that collects data at appropriate rate"""
        # Calculate sample rate based on R2 and R3 rates
        # Base clock is 204.8kHz, divided by R2 and R3
        base_clock = 204800
        sample_rate = base_clock / (self.settings["R2_rate"] * self.settings["R3_rate"])
        sample_interval = 1.0 / sample_rate

        while self.running and self.settings["enable_conversion"]:
            # Add a sample
            samples = self.data_loader.get_ecg_samples(1)
            self.data_buffer.extend(samples)

            # Check if we need to add a sync mark (every 1 second)
            current_time = time.time()
            if current_time - self.last_sync_time >= 1.0:
                self.sync_num += 1
                self.data_buffer.append([SYNC_MARK_MAGIC_NUM, self.sync_num, 0])
                self.last_sync_time = current_time

            # Limit buffer size
            if len(self.data_buffer) > 30000:
                self.data_buffer = self.data_buffer[-30000:]

            time.sleep(sample_interval)

    def process_command(self, command: Dict[str, Any]) -> str:
        """Process an ECG command and return response"""
        cmd_type = command.get("type", "")

        if cmd_type == "settings":
            return self._handle_settings(command)
        elif cmd_type == "get_data":
            return self._handle_get_data()
        elif cmd_type == "check_electrodes":
            return self._handle_check_electrodes()
        else:
            return json.dumps({"type": "error JSON"})

    def _handle_settings(self, command: Dict[str, Any]) -> str:
        """Handle settings command"""
        old_conversion = self.settings["enable_conversion"]

        if "power_enable" in command:
            self.settings["power_enable"] = command["power_enable"]
        if "enable_conversion" in command:
            self.settings["enable_conversion"] = command["enable_conversion"]
        if "R2_rate" in command:
            self.settings["R2_rate"] = command["R2_rate"]
        if "R3_rate" in command:
            self.settings["R3_rate"] = command["R3_rate"]

        # Start or stop data collection based on settings
        if self.settings["power_enable"] and self.settings["enable_conversion"]:
            if not old_conversion:
                self.data_buffer.clear()
                self.start_data_collection()
        else:
            self.stop_data_collection()

        # Return actual settings (echo back the settings)
        response = {
            "type": "actual_settings",
            "power_enable": self.settings["power_enable"],
            "enable_conversion": self.settings["enable_conversion"],
            "R2_rate": self.settings["R2_rate"],
            "R3_rate": self.settings["R3_rate"]
        }
        return json.dumps(response)

    def _handle_get_data(self) -> str:
        """Handle get_data command"""
        # Get all buffered data
        data = self.data_buffer.copy()
        self.data_buffer.clear()

        # If not collecting, simulate some data
        if not self.running or not self.settings["enable_conversion"]:
            data = self.data_loader.get_ecg_samples(50)

        response = {
            "type": "data",
            "data_size": len(data),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "data": data
        }
        return json.dumps(response)

    def _handle_check_electrodes(self) -> str:
        """Handle check_electrodes command"""
        response = {
            "type": "check_electrodes",
            "status": "connected"
        }
        return json.dumps(response)


class ICGMockHandler:
    """Handles ICG (MAX30009) mock commands"""

    def __init__(self, data_loader: MockDataLoader):
        self.data_loader = data_loader
        self.settings = {
            "measure_enable": False,
            "stimulate_frequency": 10000,
            "measure_frequency": 5,
            "stimulate_current": "64uA",
            "input_HP_filter": "BYPASS",
            "out_HP_filter": "BYPASS",
            "out_LP_filter": "BYPASS",
            "gain": "x5"
        }
        self.is_measuring = False
        self.is_calibrating = False
        self.sync_num = 0
        self.last_sync_time = time.time()
        self.data_buffer: List[List[int]] = []
        self.running = False
        self.data_thread: Optional[threading.Thread] = None
        self.pending_state_messages: List[str] = []
        self.base_table_built = False

    def start_data_collection(self):
        """Start background data collection thread"""
        if self.running:
            return
        self.running = True
        self.data_thread = threading.Thread(target=self._collect_data, daemon=True)
        self.data_thread.start()

    def stop_data_collection(self):
        """Stop background data collection"""
        self.running = False
        self.is_measuring = False
        if self.data_thread:
            self.data_thread.join(timeout=1.0)
            self.data_thread = None

    def _collect_data(self):
        """Background thread that collects data at measure_frequency"""
        sample_interval = 1.0 / self.settings["measure_frequency"]

        while self.running and self.is_measuring:
            # Add a sample
            samples = self.data_loader.get_icg_samples(1)
            self.data_buffer.extend(samples)

            # Check if we need to add a sync mark (every 1 second)
            current_time = time.time()
            if current_time - self.last_sync_time >= 1.0:
                self.sync_num += 1
                # ICG sync mark format: [-999990000, sync_num*10000, 0, 0, 0]
                self.data_buffer.append([ICG_SYNC_MARK_MAGIC_NUM, self.sync_num * 10000, 0, 0, 0])
                self.last_sync_time = current_time

            # Limit buffer size
            if len(self.data_buffer) > 30000:
                self.data_buffer = self.data_buffer[-30000:]

            time.sleep(sample_interval)

    def process_command(self, command: Dict[str, Any]) -> str:
        """Process an ICG command and return response"""
        cmd_type = command.get("type", "")

        if cmd_type == "settings":
            return self._handle_settings(command)
        elif cmd_type == "get_data":
            return self._handle_get_data()
        elif cmd_type == "build_base_table":
            return self._handle_build_base_table()
        elif cmd_type == "poweroff":
            return self._handle_poweroff()
        else:
            return json.dumps({"type": "error JSON"})

    def _handle_settings(self, command: Dict[str, Any]) -> str:
        """Handle settings command - starts the measurement state machine"""
        measure_enable = command.get("measure_enable", False)

        if measure_enable:
            # If already measuring, ignore new configuration request
            if self.is_measuring or self.settings["measure_enable"]:
                return json.dumps({
                    "type": "error",
                    "message": "Already measuring. Stop measurement first with measure_enable: false"
                })

            # Update settings only when starting new measurement
            if "stimulate_frequency" in command:
                self.settings["stimulate_frequency"] = command["stimulate_frequency"]
            if "measure_frequency" in command:
                self.settings["measure_frequency"] = command["measure_frequency"]
            if "stimulate_current" in command:
                self.settings["stimulate_current"] = command["stimulate_current"]
            if "input_HP_filter" in command:
                self.settings["input_HP_filter"] = command["input_HP_filter"]
            if "out_HP_filter" in command:
                self.settings["out_HP_filter"] = command["out_HP_filter"]
            if "out_LP_filter" in command:
                self.settings["out_LP_filter"] = command["out_LP_filter"]

            # Start the measurement state machine sequence
            self.settings["measure_enable"] = True

            # Queue up the state messages to be sent
            self.pending_state_messages = [
                json.dumps({"type": "meas_state", "state": "pre_measuring"}),
                json.dumps({"type": "meas_state", "state": "pre_measure_end", "real": 990}),
                json.dumps({"type": "meas_state", "state": "calibrating"}),
                json.dumps({"type": "meas_state", "state": "calibrate_end"}),
                json.dumps({"type": "meas_state", "state": "start_measuring"}),
            ]

            # Start a thread to send state messages and then start measuring
            threading.Thread(target=self._send_state_sequence, daemon=True).start()

            # Return first state message immediately
            return self.pending_state_messages.pop(0)
        else:
            # Stop measuring
            self.settings["measure_enable"] = False
            self.stop_data_collection()

            response = {
                "type": "actual_settings",
                "gain": self.settings["gain"],
                "input_HP_filter": self.settings["input_HP_filter"],
                "measure_enable": self.settings["measure_enable"],
                "measure_frequency": self.settings["measure_frequency"],
                "out_HP_filter": self.settings["out_HP_filter"],
                "out_LP_filter": self.settings["out_LP_filter"],
                "stimulate_current": self.settings["stimulate_current"],
                "stimulate_frequency": self.settings["stimulate_frequency"]
            }
            return json.dumps(response)

    def _send_state_sequence(self):
        """Send state sequence messages with delays (~2 seconds total)"""
        # Send remaining state messages with 0.3 second delays (~1.5 seconds for 5 messages)
        for msg in self.pending_state_messages:
            time.sleep(0.3)
            # The message will be picked up by get_pending_message()

        self.pending_state_messages.clear()

        # Short delay before starting measurement
        time.sleep(0.5)
        self.is_measuring = True
        self.data_buffer.clear()
        self.start_data_collection()

    def get_pending_messages(self) -> List[str]:
        """Get any pending asynchronous messages"""
        messages = []
        if self.pending_state_messages:
            messages.append(self.pending_state_messages.pop(0))
        return messages

    def _handle_get_data(self) -> str:
        """Handle get_data command"""
        if not self.is_measuring:
            return json.dumps({"type": "no_measure"})

        # Get all buffered data
        data = self.data_buffer.copy()
        self.data_buffer.clear()

        # If no data, get some samples
        if not data:
            data = self.data_loader.get_icg_samples(self.settings["measure_frequency"])

        response = {
            "type": "data",
            "data_frequency": self.settings["measure_frequency"],
            "data_size": len(data),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "data": data
        }
        return json.dumps(response)

    def _handle_build_base_table(self) -> str:
        """Handle build_base_table command - run once at startup"""
        self.base_table_built = True
        # In a real implementation, this would trigger calibration data generation
        # For mock, we just acknowledge
        return json.dumps({"type": "build_base_table_started"})

    def _handle_poweroff(self) -> str:
        """Handle poweroff command"""
        self.stop_data_collection()
        self.settings["measure_enable"] = False
        return json.dumps({"type": "power_is_off"})


class MockTCPServer:
    """TCP server for handling JSON commands"""

    def __init__(self, port: int, handler, name: str):
        self.port = port
        self.handler = handler
        self.name = name
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.server_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the TCP server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)

        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()

        print(f"{self.name} Mock Server started on port {self.port}")

    def stop(self):
        """Stop the TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread:
            self.server_thread.join(timeout=2.0)
        print(f"{self.name} Mock Server stopped")

    def _server_loop(self):
        """Main server loop accepting connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"{self.name}: Connection accepted from {address[0]}:{address[1]}")

                # Send connection accepted message
                client_socket.send(b"Connection accepted\n")

                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"{self.name}: Server error: {e}")

    def _handle_client(self, client_socket: socket.socket):
        """Handle a single client connection"""
        client_socket.settimeout(0.1)
        buffer = ""
        waiting_for_async = False
        async_settings_sent = False

        while self.running:
            # Check for pending async messages (ICG state sequence)
            if hasattr(self.handler, 'get_pending_messages'):
                messages = self.handler.get_pending_messages()
                for msg in messages:
                    print(f"{self.name} ASYNC OUT: {msg}")
                    try:
                        client_socket.send(msg.encode('utf-8') + b'\n')
                    except:
                        break
                    waiting_for_async = True
                    async_settings_sent = False

                # Check if state sequence finished and measurement started
                if waiting_for_async and self.handler.is_measuring and not async_settings_sent:
                    actual_settings = {
                        "type": "actual_settings",
                        "gain": self.handler.settings["gain"],
                        "input_HP_filter": self.handler.settings["input_HP_filter"],
                        "measure_enable": self.handler.settings["measure_enable"],
                        "measure_frequency": self.handler.settings["measure_frequency"],
                        "out_HP_filter": self.handler.settings["out_HP_filter"],
                        "out_LP_filter": self.handler.settings["out_LP_filter"],
                        "stimulate_current": self.handler.settings["stimulate_current"],
                        "stimulate_frequency": self.handler.settings["stimulate_frequency"]
                    }
                    settings_json = json.dumps(actual_settings)
                    print(f"{self.name} ASYNC OUT: {settings_json}")
                    try:
                        client_socket.send(settings_json.encode('utf-8') + b'\n')
                    except:
                        break
                    async_settings_sent = True
                    waiting_for_async = False

            try:
                data = client_socket.recv(2048)
                if not data:
                    break

                buffer += data.decode('utf-8')

                # Process complete JSON messages (newline-delimited)
                while '\n' in buffer or buffer.strip():
                    # Try to find a complete JSON object
                    if '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                    else:
                        line = buffer
                        buffer = ""

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        command = json.loads(line)
                        print(f"{self.name} IN: {line}")

                        response = self.handler.process_command(command)
                        print(f"{self.name} OUT: {response}")

                        client_socket.send(response.encode('utf-8') + b'\n')

                        # If this was an ICG settings command with measure_enable=true,
                        # mark that we're waiting for async messages
                        if hasattr(self.handler, 'is_measuring'):
                            if command.get('type') == 'settings' and command.get('measure_enable'):
                                waiting_for_async = True
                                async_settings_sent = False

                    except json.JSONDecodeError:
                        error_response = json.dumps({"type": "error JSON"})
                        client_socket.send(error_response.encode('utf-8') + b'\n')

                    break  # Process one command at a time

            except socket.timeout:
                continue
            except Exception as e:
                print(f"{self.name}: Client error: {e}")
                break

        client_socket.close()
        print(f"{self.name}: Client disconnected")


def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Mock SPI_DEV_servise for ECG and ICG sensors')
    parser.add_argument('--sample-data', '-s', type=str, default=None,
                        help='Path to sample_data.txt file')
    args = parser.parse_args()

    print("=" * 60)
    print("Mock SPI_DEV_servise")
    print("=" * 60)
    print()

    # Check if ports are available (i.e., real service is not running)
    ecg_in_use = not check_port_available(ECG_PORT)
    icg_in_use = not check_port_available(ICG_PORT)

    if ecg_in_use or icg_in_use:
        print("ERROR: Ports are already in use!")
        print()
        if ecg_in_use:
            print(f"  Port {ECG_PORT} (ECG) is in use")
        if icg_in_use:
            print(f"  Port {ICG_PORT} (ICG) is in use")
        print()
        print("The real SPI_DEV_servise may be running. To stop it:")
        print()
        print("  Option 1: Kill by process name")
        print("    pkill -f SPI_DEV_servise")
        print()
        print("  Option 2: Find and kill by port")
        print(f"    sudo lsof -i :{ECG_PORT}")
        print(f"    sudo kill <PID>")
        print()
        print("  Option 3: If running as systemd service")
        print("    sudo systemctl stop spi_dev_service")
        print()
        sys.exit(1)

    # Load sample data
    data_loader = MockDataLoader(args.sample_data)

    # Create handlers
    ecg_handler = ECGMockHandler(data_loader)
    icg_handler = ICGMockHandler(data_loader)

    # Create and start servers
    ecg_server = MockTCPServer(ECG_PORT, ecg_handler, "ECG")
    icg_server = MockTCPServer(ICG_PORT, icg_handler, "ICG")

    ecg_server.start()
    icg_server.start()

    print()
    print("Mock services running:")
    print(f"  ECG (ADS1293) on port {ECG_PORT}")
    print(f"  ICG (MAX30009) on port {ICG_PORT}")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nShutting down...")

    ecg_server.stop()
    icg_server.stop()
    print("Mock services stopped")


if __name__ == "__main__":
    main()
