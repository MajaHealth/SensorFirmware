#!/usr/bin/env python3
"""
ICG-ECG Drift Results Plotting Script

This script generates plots from the drift test data collected by test_icg_ecg_drift_1hour.py.
Run this on your local machine after copying the CSV/JSON files from the embedded device.

Requirements:
    pip3 install matplotlib numpy pandas

Usage:
    python3 plot_drift_results.py <csv_file>
    python3 plot_drift_results.py <json_file>

Examples:
    python3 plot_drift_results.py icg_ecg_drift_1hour_20251028_103000.csv
    python3 plot_drift_results.py icg_ecg_drift_1hour_results_20251028_103000.json

Output:
    - drift_over_time_<timestamp>.png
    - sample_count_validation_<timestamp>.png
    - drift_histogram_<timestamp>.png
"""

import sys
import json
import os
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
except ImportError as e:
    print("Error: Required plotting libraries not installed.")
    print("Please install with: pip3 install matplotlib numpy pandas")
    print(f"Missing: {e}")
    sys.exit(1)


def load_data_from_csv(csv_file):
    """Load drift data from CSV file

    Args:
        csv_file: Path to CSV file

    Returns:
        tuple: (df, config_dict) where df is pandas DataFrame and config_dict has test config
    """
    print(f"Loading data from CSV: {csv_file}")

    # Load CSV
    df = pd.read_csv(csv_file)

    # Extract configuration from filename or use defaults
    config = {
        'sync_threshold_ms': 50.0,  # Default
        'expected_samples': 400,
        'icg_sampling_rate': 400,
        'ecg_sampling_rate': 400
    }

    print(f"  ✓ Loaded {len(df)} data points")

    return df, config


def load_data_from_json(json_file):
    """Load drift data from JSON file

    Args:
        json_file: Path to JSON file

    Returns:
        tuple: (df, config_dict) where df is pandas DataFrame and config_dict has test config
    """
    print(f"Loading data from JSON: {json_file}")

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract drift data
    drift_data = data['results']['drift_data']

    # Convert to DataFrame
    df = pd.DataFrame(drift_data)

    # Extract configuration
    config = {
        'sync_threshold_ms': data['configuration']['sync_threshold_ms'],
        'expected_samples': data['results']['statistics']['expected_samples'],
        'icg_sampling_rate': data['configuration']['icg_sampling_rate'],
        'ecg_sampling_rate': data['configuration']['ecg_sampling_rate'],
        'statistics': data['results']['statistics']
    }

    print(f"  ✓ Loaded {len(df)} data points")

    return df, config


def generate_drift_over_time_plot(df, config, output_filename):
    """Generate drift over time plot

    Args:
        df: DataFrame with drift data
        config: Configuration dictionary
        output_filename: Output filename for plot
    """
    print(f"  Generating: {output_filename}")

    # Convert elapsed time to minutes
    elapsed_times_min = df['elapsed_time_s'] / 60
    time_diffs = df['time_diff_ms']

    plt.figure(figsize=(12, 6))

    # Plot raw data
    plt.plot(elapsed_times_min, time_diffs, 'b-', linewidth=0.5, alpha=0.6, label='Time Difference')

    # Add trend line
    if len(elapsed_times_min) > 1:
        z = np.polyfit(elapsed_times_min, time_diffs, 1)
        p = np.poly1d(z)
        drift_rate_per_hour = z[0] * 60  # Convert per-minute to per-hour
        plt.plot(elapsed_times_min, p(elapsed_times_min), "r--", linewidth=2,
                label=f'Trend (drift: {drift_rate_per_hour:.3f} ms/hour)')

    # Add threshold line
    threshold = config['sync_threshold_ms']
    plt.axhline(y=threshold, color='orange', linestyle='--',
               linewidth=2, label=f'Threshold ({threshold} ms)')

    # Add mean line
    mean_drift = time_diffs.mean()
    plt.axhline(y=mean_drift, color='green', linestyle=':', linewidth=1.5,
               alpha=0.7, label=f'Mean ({mean_drift:.2f} ms)')

    plt.xlabel('Elapsed Time (minutes)', fontsize=12)
    plt.ylabel('Time Difference (ms)', fontsize=12)
    plt.title('ICG-ECG Synchronization Drift Over Time', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_filename, dpi=150)
    plt.close()

    print(f"    ✓ Saved: {output_filename}")


def generate_sample_count_plot(df, config, output_filename):
    """Generate sample count validation plot

    Args:
        df: DataFrame with drift data
        config: Configuration dictionary
        output_filename: Output filename for plot
    """
    print(f"  Generating: {output_filename}")

    # Filter out None values
    df_valid = df[df['icg_samples_between'].notna() & df['ecg_samples_between'].notna()].copy()

    if len(df_valid) == 0:
        print("    ⚠ No valid sample count data to plot")
        return

    elapsed_times_min = df_valid['elapsed_time_s'] / 60
    icg_samples = df_valid['icg_samples_between']
    ecg_samples = df_valid['ecg_samples_between']
    expected_samples = config['expected_samples']

    plt.figure(figsize=(12, 6))

    # Plot sample counts
    plt.plot(elapsed_times_min, icg_samples, 'b-', linewidth=0.5, alpha=0.6, label='ICG Samples')
    plt.plot(elapsed_times_min, ecg_samples, 'g-', linewidth=0.5, alpha=0.6, label='ECG Samples')

    # Add expected value line
    plt.axhline(y=expected_samples, color='r', linestyle='--',
               linewidth=2, label=f'Expected ({expected_samples} samples)')

    # Add tolerance bands (±5%)
    plt.axhline(y=expected_samples * 1.05, color='orange',
               linestyle=':', linewidth=1, alpha=0.5, label='±5% tolerance')
    plt.axhline(y=expected_samples * 0.95, color='orange',
               linestyle=':', linewidth=1, alpha=0.5)

    # Fill tolerance band
    plt.fill_between(elapsed_times_min,
                     expected_samples * 0.95,
                     expected_samples * 1.05,
                     alpha=0.1, color='yellow')

    plt.xlabel('Elapsed Time (minutes)', fontsize=12)
    plt.ylabel('Samples Between Sync Marks', fontsize=12)
    plt.title(f'Sample Count Validation (Expected: {expected_samples} samples @ {config["icg_sampling_rate"]} Hz)',
             fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_filename, dpi=150)
    plt.close()

    print(f"    ✓ Saved: {output_filename}")


def generate_drift_histogram(df, config, output_filename):
    """Generate drift distribution histogram

    Args:
        df: DataFrame with drift data
        config: Configuration dictionary
        output_filename: Output filename for plot
    """
    print(f"  Generating: {output_filename}")

    time_diffs = df['time_diff_ms']

    plt.figure(figsize=(10, 6))

    # Create histogram
    n, bins, patches = plt.hist(time_diffs, bins=50, color='blue', alpha=0.7, edgecolor='black')

    # Add threshold line
    threshold = config['sync_threshold_ms']
    plt.axvline(x=threshold, color='r', linestyle='--',
               linewidth=2, label=f'Threshold ({threshold} ms)')

    # Add mean line
    mean_drift = time_diffs.mean()
    plt.axvline(x=mean_drift, color='green', linestyle='-',
               linewidth=2, label=f'Mean ({mean_drift:.2f} ms)')

    # Add median line
    median_drift = time_diffs.median()
    plt.axvline(x=median_drift, color='purple', linestyle='-',
               linewidth=2, alpha=0.7, label=f'Median ({median_drift:.2f} ms)')

    # Add statistics text box
    stats_text = f'Statistics:\n'
    stats_text += f'Mean: {mean_drift:.2f} ms\n'
    stats_text += f'Median: {median_drift:.2f} ms\n'
    stats_text += f'Std Dev: {time_diffs.std():.2f} ms\n'
    stats_text += f'Min: {time_diffs.min():.2f} ms\n'
    stats_text += f'Max: {time_diffs.max():.2f} ms\n'
    stats_text += f'Count: {len(time_diffs)}'

    plt.text(0.98, 0.97, stats_text,
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.xlabel('Time Difference (ms)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of ICG-ECG Time Differences', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_filename, dpi=150)
    plt.close()

    print(f"    ✓ Saved: {output_filename}")


def print_statistics(df, config):
    """Print summary statistics

    Args:
        df: DataFrame with drift data
        config: Configuration dictionary
    """
    print("\n" + "="*80)
    print("DRIFT STATISTICS SUMMARY")
    print("="*80)

    time_diffs = df['time_diff_ms']

    print(f"\nDrift Statistics:")
    print(f"  Count: {len(time_diffs)}")
    print(f"  Mean: {time_diffs.mean():.3f} ms")
    print(f"  Median: {time_diffs.median():.3f} ms")
    print(f"  Std Dev: {time_diffs.std():.3f} ms")
    print(f"  Min: {time_diffs.min():.3f} ms")
    print(f"  Max: {time_diffs.max():.3f} ms")
    print(f"  25th percentile: {time_diffs.quantile(0.25):.3f} ms")
    print(f"  75th percentile: {time_diffs.quantile(0.75):.3f} ms")

    # Calculate drift rate
    if len(df) > 1:
        elapsed_times = df['elapsed_time_s'].values
        drifts = time_diffs.values
        z = np.polyfit(elapsed_times, drifts, 1)
        drift_rate = z[0] * 3600  # ms per hour
        print(f"  Drift rate: {drift_rate:.3f} ms/hour")

    # Sample count statistics
    if 'icg_samples_between' in df.columns:
        icg_samples = df['icg_samples_between'].dropna()
        ecg_samples = df['ecg_samples_between'].dropna()

        if len(icg_samples) > 0:
            print(f"\nICG Sample Count:")
            print(f"  Mean: {icg_samples.mean():.1f}")
            print(f"  Std Dev: {icg_samples.std():.1f}")
            print(f"  Min: {int(icg_samples.min())}")
            print(f"  Max: {int(icg_samples.max())}")

        if len(ecg_samples) > 0:
            print(f"\nECG Sample Count:")
            print(f"  Mean: {ecg_samples.mean():.1f}")
            print(f"  Std Dev: {ecg_samples.std():.1f}")
            print(f"  Min: {int(ecg_samples.min())}")
            print(f"  Max: {int(ecg_samples.max())}")

        expected = config.get('expected_samples', 400)
        if len(icg_samples) > 0:
            icg_deviation_pct = abs(icg_samples.mean() - expected) / expected * 100
            print(f"  ICG deviation from expected: {icg_deviation_pct:.2f}%")
        if len(ecg_samples) > 0:
            ecg_deviation_pct = abs(ecg_samples.mean() - expected) / expected * 100
            print(f"  ECG deviation from expected: {ecg_deviation_pct:.2f}%")

    # Check against threshold
    threshold = config['sync_threshold_ms']
    exceeds_threshold = time_diffs[time_diffs > threshold]
    if len(exceeds_threshold) > 0:
        print(f"\n⚠ WARNING: {len(exceeds_threshold)} values exceed threshold ({threshold} ms)")
        print(f"  Percentage: {len(exceeds_threshold)/len(time_diffs)*100:.1f}%")
    else:
        print(f"\n✓ PASS: All values within threshold ({threshold} ms)")

    print("="*80)


def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print("Error: No input file specified")
        print("\nUsage:")
        print("  python3 plot_drift_results.py <csv_file>")
        print("  python3 plot_drift_results.py <json_file>")
        print("\nExamples:")
        print("  python3 plot_drift_results.py icg_ecg_drift_1hour_20251028_103000.csv")
        print("  python3 plot_drift_results.py icg_ecg_drift_1hour_results_20251028_103000.json")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print("\n" + "="*80)
    print("ICG-ECG DRIFT RESULTS PLOTTING")
    print("="*80)

    # Load data based on file type
    if input_file.endswith('.csv'):
        df, config = load_data_from_csv(input_file)
        base_name = input_file.replace('.csv', '')
    elif input_file.endswith('.json'):
        df, config = load_data_from_json(input_file)
        base_name = input_file.replace('.json', '').replace('_results', '')
    else:
        print("Error: Input file must be .csv or .json")
        sys.exit(1)

    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate plots
    print("\nGenerating plots...")

    plot1 = f"drift_over_time_{timestamp}.png"
    generate_drift_over_time_plot(df, config, plot1)

    plot2 = f"sample_count_validation_{timestamp}.png"
    generate_sample_count_plot(df, config, plot2)

    plot3 = f"drift_histogram_{timestamp}.png"
    generate_drift_histogram(df, config, plot3)

    # Print statistics
    print_statistics(df, config)

    print("\n" + "="*80)
    print("PLOTS GENERATED SUCCESSFULLY")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  - {plot1}")
    print(f"  - {plot2}")
    print(f"  - {plot3}")
    print("="*80)


if __name__ == "__main__":
    main()
