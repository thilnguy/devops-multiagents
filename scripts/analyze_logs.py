#!/usr/bin/env python3
"""
Smart Log Analyzer & Clusterer
Groups similar log lines to reduce token usage for LLMs.
"""

import sys
import re
import argparse
from collections import defaultdict
from typing import Dict, List, Tuple

def tokenize_line(line: str) -> str:
    """
    Replace variable parts of a log line (timestamps, IPs, numbers) with placeholders
    to identify the underlying pattern.
    """
    # Remove Timestamp (ISO8601, standard formats)
    line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', '<TIMESTAMP>', line)
    
    # Remove UUIDs
    line = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '<UUID>', line)
    
    # Remove IP addresses
    line = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '<IP>', line)
    
    # Remove Hex numbers (common in memory addresses)
    line = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', line)
    
    # Remove generic numbers (careful not to kill error codes)
    # We keep numbers if they are short, but replacing long sequences
    line = re.sub(r'\b\d{5,}\b', '<NUM>', line)

    return line.strip()

def analyze_logs(file_path: str, show_info: bool = False) -> None:
    """
    Read log file, cluster lines, and print summary.
    """
    clusters: Dict[str, Dict] = defaultdict(lambda: {'count': 0, 'sample': ''})
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Filter Noise if not requested
                if not show_info and ('INFO' in line or 'DEBUG' in line):
                    continue

                pattern = tokenize_line(line)
                
                if clusters[pattern]['count'] == 0:
                    clusters[pattern]['sample'] = line
                
                clusters[pattern]['count'] += 1
                
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Sort by frequency (descending)
    sorted_clusters = sorted(clusters.items(), key=lambda x: x[1]['count'], reverse=True)

    print(f"=== Log Analysis Summary: {file_path} ===\n")
    print(f"Total Unique Patterns: {len(sorted_clusters)}")
    print("-" * 60)
    
    for pattern, data in sorted_clusters:
        count = data['count']
        sample = data['sample']
        
        # Truncate very long lines
        if len(sample) > 200:
            sample = sample[:197] + "..."
            
        print(f"[{count}x] {sample}")

    print("-" * 60)
    if not show_info:
        print("(Note: INFO and DEBUG logs were hidden. Use --all to see them.)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Clustering Tool for LLM Efficiency")
    parser.add_argument("file", help="Path to the log file")
    parser.add_argument("--all", action="store_true", help="Include INFO and DEBUG logs")
    
    args = parser.parse_args()
    analyze_logs(args.file, args.all)
