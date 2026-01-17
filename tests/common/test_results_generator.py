#!/usr/bin/env python3
"""
Test Results Generator

Automatically generates comprehensive test result reports with:
- Pass/Fail status for each step
- Timestamps
- Test metadata
- Summary statistics
"""

import os
import json
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class StepStatus(Enum):
    """Status of a test step"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    PENDING = "PENDING"


class TestStep:
    """Represents a single test step"""

    def __init__(self, step_number: int, name: str, description: str = ""):
        self.step_number = step_number
        self.name = name
        self.description = description
        self.status = StepStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.details: str = ""
        self.error_message: str = ""

    def start(self):
        """Mark step as started"""
        self.start_time = datetime.now()

    def passed(self, details: str = ""):
        """Mark step as passed"""
        self.status = StepStatus.PASS
        self.end_time = datetime.now()
        self.details = details

    def failed(self, error_message: str = "", details: str = ""):
        """Mark step as failed"""
        self.status = StepStatus.FAIL
        self.end_time = datetime.now()
        self.error_message = error_message
        self.details = details

    def skipped(self, reason: str = ""):
        """Mark step as skipped"""
        self.status = StepStatus.SKIP
        self.end_time = datetime.now()
        self.details = reason

    @property
    def duration(self) -> float:
        """Get step duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'step_number': self.step_number,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'details': self.details,
            'error_message': self.error_message,
        }


class ResultsGenerator:
    """
    Generates comprehensive test result reports.

    Usage:
        results = TestResultsGenerator(
            test_id="030",
            test_name="CM4 Enumeration on PC",
            category="HW Component Test"
        )

        step1 = results.add_step(1, "Check Prerequisites")
        step1.start()
        # ... do work ...
        step1.passed("rpiboot is installed")

        results.save_results()
    """

    def __init__(
        self,
        test_id: str,
        test_name: str,
        category: str = "Unit Test",
        output_dir: str = "/tmp/test-results"
    ):
        self.test_id = test_id
        self.test_name = test_name
        self.category = category
        self.output_dir = output_dir

        self.steps: List[TestStep] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.overall_status = StepStatus.PENDING

        # Test metadata
        self.metadata: Dict[str, Any] = {
            'platform': self._get_platform(),
            'python_version': self._get_python_version(),
            'tester': os.environ.get('USER', 'unknown'),
        }

        # Acceptance criteria
        self.acceptance_criteria: List[Dict[str, Any]] = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def _get_platform(self) -> str:
        """Get platform info"""
        import platform
        return f"{platform.system()} {platform.release()}"

    def _get_python_version(self) -> str:
        """Get Python version"""
        import sys
        return sys.version.split()[0]

    def start_test(self):
        """Mark test as started"""
        self.start_time = datetime.now()
        print(f"\n{'=' * 70}")
        print(f"Test Case #{self.test_id}: {self.test_name}")
        print(f"{'=' * 70}")
        print(f"\n{self.category}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 70}")

    def add_step(self, step_number: int, name: str, description: str = "") -> TestStep:
        """Add a test step"""
        step = TestStep(step_number, name, description)
        self.steps.append(step)
        return step

    def add_acceptance_criterion(self, criterion: str, expected: str):
        """Add an acceptance criterion"""
        self.acceptance_criteria.append({
            'criterion': criterion,
            'expected': expected,
            'status': StepStatus.PENDING.value,
            'actual': '',
        })

    def update_acceptance_criterion(self, criterion: str, actual: str, passed: bool):
        """Update acceptance criterion result"""
        for ac in self.acceptance_criteria:
            if ac['criterion'] == criterion:
                ac['actual'] = actual
                ac['status'] = StepStatus.PASS.value if passed else StepStatus.FAIL.value
                break

    def finish_test(self, passed: bool, summary: str = ""):
        """Mark test as finished"""
        self.end_time = datetime.now()
        self.overall_status = StepStatus.PASS if passed else StepStatus.FAIL

        # Auto-save results
        self.save_results()

        # Print summary
        self._print_summary(summary)

    def _print_summary(self, summary: str = ""):
        """Print test summary to console"""
        print(f"\n{'=' * 70}")
        print(f"TEST RESULT: {self.overall_status.value}")
        print(f"{'=' * 70}")

        print(f"\nTest: #{self.test_id} - {self.test_name}")
        print(f"Duration: {self.duration:.2f} seconds")
        print(f"Finished: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Step summary
        print(f"\n{'─' * 70}")
        print("STEP RESULTS:")
        print(f"{'─' * 70}")

        for step in self.steps:
            status_icon = "PASS" if step.status == StepStatus.PASS else \
                          "FAIL" if step.status == StepStatus.FAIL else \
                          "SKIP" if step.status == StepStatus.SKIP else "----"
            print(f"  Step {step.step_number}: {step.name:<40} [{status_icon}]")
            if step.error_message:
                print(f"           Error: {step.error_message}")

        # Acceptance criteria
        if self.acceptance_criteria:
            print(f"\n{'─' * 70}")
            print("ACCEPTANCE CRITERIA:")
            print(f"{'─' * 70}")

            for ac in self.acceptance_criteria:
                status_icon = "PASS" if ac['status'] == 'PASS' else \
                              "FAIL" if ac['status'] == 'FAIL' else "----"
                print(f"  [{status_icon}] {ac['criterion']}")
                if ac['actual']:
                    print(f"         Expected: {ac['expected']}")
                    print(f"         Actual:   {ac['actual']}")

        # Statistics
        passed_steps = sum(1 for s in self.steps if s.status == StepStatus.PASS)
        failed_steps = sum(1 for s in self.steps if s.status == StepStatus.FAIL)
        skipped_steps = sum(1 for s in self.steps if s.status == StepStatus.SKIP)

        print(f"\n{'─' * 70}")
        print("STATISTICS:")
        print(f"{'─' * 70}")
        print(f"  Total Steps:   {len(self.steps)}")
        print(f"  Passed:        {passed_steps}")
        print(f"  Failed:        {failed_steps}")
        print(f"  Skipped:       {skipped_steps}")

        if summary:
            print(f"\n{'─' * 70}")
            print("SUMMARY:")
            print(f"{'─' * 70}")
            print(f"  {summary}")

        # Report location
        print(f"\n{'─' * 70}")
        print("REPORT FILES:")
        print(f"{'─' * 70}")
        print(f"  Text Report: {self._get_text_report_path()}")
        print(f"  JSON Report: {self._get_json_report_path()}")
        print(f"{'=' * 70}\n")

    @property
    def duration(self) -> float:
        """Get test duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def _get_text_report_path(self) -> str:
        """Get text report file path"""
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S') if self.start_time else 'unknown'
        return os.path.join(self.output_dir, f"test_{self.test_id}_{timestamp}_report.txt")

    def _get_json_report_path(self) -> str:
        """Get JSON report file path"""
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S') if self.start_time else 'unknown'
        return os.path.join(self.output_dir, f"test_{self.test_id}_{timestamp}_report.json")

    def save_results(self):
        """Save test results to files"""
        self._save_text_report()
        self._save_json_report()
        self._save_latest_symlink()

    def _save_text_report(self):
        """Save human-readable text report"""
        report_path = self._get_text_report_path()

        with open(report_path, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write(f"TEST RESULT REPORT\n")
            f.write("=" * 70 + "\n\n")

            # Test Info
            f.write(f"Test ID:      #{self.test_id}\n")
            f.write(f"Test Name:    {self.test_name}\n")
            f.write(f"Category:     {self.category}\n")
            f.write(f"Status:       {self.overall_status.value}\n")
            f.write(f"Duration:     {self.duration:.2f} seconds\n")
            f.write(f"\n")
            f.write(f"Start Time:   {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'N/A'}\n")
            f.write(f"End Time:     {self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'N/A'}\n")
            f.write(f"\n")

            # Metadata
            f.write("-" * 70 + "\n")
            f.write("ENVIRONMENT:\n")
            f.write("-" * 70 + "\n")
            for key, value in self.metadata.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")

            # Steps
            f.write("-" * 70 + "\n")
            f.write("TEST STEPS:\n")
            f.write("-" * 70 + "\n\n")

            for step in self.steps:
                status_str = f"[{step.status.value}]"
                f.write(f"Step {step.step_number}: {step.name} {status_str}\n")
                if step.description:
                    f.write(f"  Description: {step.description}\n")
                if step.start_time:
                    f.write(f"  Start Time:  {step.start_time.strftime('%H:%M:%S.%f')[:-3]}\n")
                if step.end_time:
                    f.write(f"  End Time:    {step.end_time.strftime('%H:%M:%S.%f')[:-3]}\n")
                f.write(f"  Duration:    {step.duration:.3f}s\n")
                if step.details:
                    f.write(f"  Details:     {step.details}\n")
                if step.error_message:
                    f.write(f"  ERROR:       {step.error_message}\n")
                f.write("\n")

            # Acceptance Criteria
            if self.acceptance_criteria:
                f.write("-" * 70 + "\n")
                f.write("ACCEPTANCE CRITERIA:\n")
                f.write("-" * 70 + "\n\n")

                for i, ac in enumerate(self.acceptance_criteria, 1):
                    f.write(f"{i}. {ac['criterion']}\n")
                    f.write(f"   Expected: {ac['expected']}\n")
                    f.write(f"   Actual:   {ac['actual']}\n")
                    f.write(f"   Status:   {ac['status']}\n\n")

            # Summary
            passed_steps = sum(1 for s in self.steps if s.status == StepStatus.PASS)
            failed_steps = sum(1 for s in self.steps if s.status == StepStatus.FAIL)
            skipped_steps = sum(1 for s in self.steps if s.status == StepStatus.SKIP)

            f.write("-" * 70 + "\n")
            f.write("SUMMARY:\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Total Steps: {len(self.steps)}\n")
            f.write(f"  Passed:      {passed_steps}\n")
            f.write(f"  Failed:      {failed_steps}\n")
            f.write(f"  Skipped:     {skipped_steps}\n")
            f.write(f"\n")
            f.write(f"  OVERALL RESULT: {self.overall_status.value}\n")
            f.write("\n")
            f.write("=" * 70 + "\n")
            f.write(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n")

    def _save_json_report(self):
        """Save JSON report for programmatic access"""
        report_path = self._get_json_report_path()

        report_data = {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'category': self.category,
            'overall_status': self.overall_status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration,
            'metadata': self.metadata,
            'steps': [step.to_dict() for step in self.steps],
            'acceptance_criteria': self.acceptance_criteria,
            'statistics': {
                'total_steps': len(self.steps),
                'passed': sum(1 for s in self.steps if s.status == StepStatus.PASS),
                'failed': sum(1 for s in self.steps if s.status == StepStatus.FAIL),
                'skipped': sum(1 for s in self.steps if s.status == StepStatus.SKIP),
            },
            'report_generated': datetime.now().isoformat(),
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

    def _save_latest_symlink(self):
        """Create symlink to latest report"""
        latest_txt = os.path.join(self.output_dir, f"test_{self.test_id}_latest_report.txt")
        latest_json = os.path.join(self.output_dir, f"test_{self.test_id}_latest_report.json")

        # Remove existing symlinks
        for path in [latest_txt, latest_json]:
            if os.path.islink(path) or os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

        # Create new symlinks
        try:
            os.symlink(self._get_text_report_path(), latest_txt)
            os.symlink(self._get_json_report_path(), latest_json)
        except:
            # Symlinks may fail on some systems, copy instead
            import shutil
            try:
                shutil.copy(self._get_text_report_path(), latest_txt)
                shutil.copy(self._get_json_report_path(), latest_json)
            except:
                pass


# Convenience function for quick test result creation
def create_test_results(test_id: str, test_name: str, category: str = "Unit Test") -> ResultsGenerator:
    """Create a new test results generator"""
    return ResultsGenerator(test_id, test_name, category)


# Alias for backward compatibility
TestResultsGenerator = ResultsGenerator
