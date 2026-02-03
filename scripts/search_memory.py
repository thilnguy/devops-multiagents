#!/usr/bin/env python3
"""
Memory Search Tool (RAG Lite)
Searches the `archived_memory.json` for relevant past learnings using keyword matching.
"""

import json
import sys
import os
import argparse
from typing import List, Dict

MEMORY_DIR = ".antigravity/state"
ARCHIVE_FILE = os.path.join(MEMORY_DIR, "archived_memory.json")
ACTIVE_FILE = os.path.join(MEMORY_DIR, "memory.json")

def load_memory(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Support both array root or object with 'learnings' key
            if isinstance(data, list):
                return data
            return data.get('learnings', [])
    except json.JSONDecodeError:
        return []

def search_memory(query: str, limit: int = 5) -> None:
    """
    Search both active and archived memory for learnings matching the query.
    """
    active_learnings = load_memory(ACTIVE_FILE)
    archived_learnings = load_memory(ARCHIVE_FILE)
    
    all_learnings = active_learnings + archived_learnings
    
    # Simple Keyword Search (Case-insensitive)
    query_terms = query.lower().split()
    results = []
    
    for item in all_learnings:
        # Check if item has necessary fields
        if not isinstance(item, dict): 
            continue
            
        text = str(item.get('pattern', '')) + " " + str(item.get('resolution', '')) + " " + str(item.get('category', ''))
        text_lower = text.lower()
        
        # Score calculation: +1 for each term found
        score = sum(1 for term in query_terms if term in text_lower)
        
        if score > 0:
            results.append((score, item))
    
    # Sort by score (descending)
    results.sort(key=lambda x: x[0], reverse=True)
    
    print(f"=== Memory Search Results for '{query}' ===")
    print(f"Found {len(results)} matches. Showing top {limit}.\n")
    
    for i, (score, item) in enumerate(results[:limit], 1):
        print(f"{i}. [Score: {score}] {item.get('id', 'N/A')} ({item.get('category', 'General')})")
        print(f"   Pattern: {item.get('pattern', 'N/A')}")
        print(f"   Resolution: {item.get('resolution', 'N/A')}")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Agent Memory")
    parser.add_argument("query", help="Search keywords (e.g. 'terraform lock state')")
    parser.add_argument("--limit", type=int, default=5, help="Max results to return")
    
    args = parser.parse_args()
    search_memory(args.query, args.limit)
