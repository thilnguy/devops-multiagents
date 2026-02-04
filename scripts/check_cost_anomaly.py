#!/usr/bin/env python3
"""
Cost Anomaly Checker (Watchdog Skill)
-------------------------------------
Queries AWS Cost Explorer to detect spending anomalies.
Usage: python3 check_cost_anomaly.py [--threshold 1.2] [--days 7]

Note: Requires boto3 and AWS credentials with ce:GetCostAndUsage permission.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

# boto3 is optional if using --mock mode
BOTO3_AVAILABLE = False
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    pass

def get_cost_data(days: int = 7) -> dict:
    """Fetch cost data from AWS Cost Explorer."""
    client = boto3.client('ce', region_name='us-east-1')  # CE is only in us-east-1
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date.isoformat(),
            'End': end_date.isoformat()
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'}
        ]
    )
    
    return response

def analyze_costs(cost_data: dict, threshold: float = 1.2) -> list:
    """Detect anomalies: days where cost exceeds average * threshold."""
    results = cost_data.get('ResultsByTime', [])
    anomalies = []
    
    # Calculate daily totals
    daily_costs = []
    for day in results:
        total = sum(float(g['Metrics']['UnblendedCost']['Amount']) for g in day.get('Groups', []))
        daily_costs.append({
            'date': day['TimePeriod']['Start'],
            'cost': total
        })
    
    if len(daily_costs) < 2:
        return []
    
    # Calculate average (excluding most recent day)
    avg_cost = sum(d['cost'] for d in daily_costs[:-1]) / max(len(daily_costs) - 1, 1)
    
    # Check last day for spike
    last_day = daily_costs[-1]
    if last_day['cost'] > avg_cost * threshold:
        anomalies.append({
            'date': last_day['date'],
            'cost': round(last_day['cost'], 2),
            'average': round(avg_cost, 2),
            'ratio': round(last_day['cost'] / avg_cost, 2) if avg_cost > 0 else 0
        })
    
    return anomalies

def main():
    parser = argparse.ArgumentParser(description="AWS Cost Anomaly Checker")
    parser.add_argument("--threshold", type=float, default=1.2, 
                        help="Alert if cost exceeds average * threshold (default: 1.2 = 20%% increase)")
    parser.add_argument("--days", type=int, default=7, 
                        help="Number of days to analyze (default: 7)")
    parser.add_argument("--mock", action="store_true",
                        help="Use mock data instead of AWS API (for testing)")
    
    args = parser.parse_args()
    
    print(f"🔍 Checking cost anomalies (last {args.days} days, threshold: {args.threshold}x)")
    
    if args.mock:
        # Mock data for testing without AWS
        cost_data = {
            "ResultsByTime": [
                {"TimePeriod": {"Start": "2026-01-28"}, "Groups": [{"Metrics": {"UnblendedCost": {"Amount": "10.50"}}}]},
                {"TimePeriod": {"Start": "2026-01-29"}, "Groups": [{"Metrics": {"UnblendedCost": {"Amount": "11.20"}}}]},
                {"TimePeriod": {"Start": "2026-01-30"}, "Groups": [{"Metrics": {"UnblendedCost": {"Amount": "10.80"}}}]},
                {"TimePeriod": {"Start": "2026-01-31"}, "Groups": [{"Metrics": {"UnblendedCost": {"Amount": "25.00"}}}]},  # Spike!
            ]
        }
    else:
        if not BOTO3_AVAILABLE:
            print("Error: boto3 not installed. Run: pip install boto3")
            print("Tip: Use --mock for testing without AWS credentials.")
            sys.exit(1)
        try:
            cost_data = get_cost_data(args.days)
        except Exception as e:
            print(f"Error fetching cost data: {e}")
            sys.exit(1)
    
    anomalies = analyze_costs(cost_data, args.threshold)
    
    if anomalies:
        print("\n⚠️ COST ANOMALY DETECTED:")
        for a in anomalies:
            print(f"  Date: {a['date']}")
            print(f"  Cost: ${a['cost']} (Average: ${a['average']})")
            print(f"  Ratio: {a['ratio']}x (Threshold: {args.threshold}x)")
        sys.exit(1)
    else:
        print("\n✅ No cost anomalies detected. All spending within normal range.")
        sys.exit(0)

if __name__ == "__main__":
    main()
