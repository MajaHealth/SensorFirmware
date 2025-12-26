"""
Data logger for saving sensor data to files
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Any, List, Dict, Optional


class JSONLLogger:
    """Logger for JSONL (JSON Lines) format."""

    def __init__(self, filepath: str, test_id: str, sensor: str):
        """
        Initialize JSONL logger.

        Args:
            filepath: Output file path
            test_id: Test identifier (e.g., "test_007_bca")
            sensor: Sensor name (e.g., "ads1293", "max30009")
        """
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.filepath, 'w')
        self.test_id = test_id
        self.sensor = sensor

    def write_data(self, data: List[Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Write sensor data with timestamp and metadata.

        Args:
            data: Sensor data array (from get_data response)
            metadata: Optional metadata (e.g., freq_khz, bpm, current)
        """
        entry = {
            'test_id': self.test_id,
            'timestamp': datetime.now().isoformat(),
            'sensor': self.sensor,
            'data': data
        }

        # Add optional metadata
        if metadata:
            entry.update(metadata)

        json_line = json.dumps(entry)
        self.file.write(json_line + '\n')
        self.file.flush()

    def write_raw(self, data: Any):
        """
        Write arbitrary data as JSON line.

        Args:
            data: Data to write (will be JSON serialized)
        """
        json_line = json.dumps(data)
        self.file.write(json_line + '\n')
        self.file.flush()

    def close(self):
        """Close the log file."""
        if self.file:
            self.file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class CSVLogger:
    """Logger for CSV format (for simple tabular data)."""

    def __init__(self, filepath: str, headers: List[str]):
        """
        Initialize CSV logger.

        Args:
            filepath: Output file path
            headers: Column headers
        """
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.filepath, 'w')
        self.headers = headers

        # Write header row
        self.file.write(','.join(headers) + '\n')
        self.file.flush()

    def write_row(self, values: List[Any]):
        """
        Write a row of data.

        Args:
            values: Values matching header columns
        """
        row = ','.join(str(v) for v in values)
        self.file.write(row + '\n')
        self.file.flush()

    def close(self):
        """Close the log file."""
        if self.file:
            self.file.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
