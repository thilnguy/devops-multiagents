#!/usr/bin/env python3
"""
Memory Search Tool (RAG with Vector Search)
Searches the `archived_memory.json` for relevant past learnings.
Supports keyword matching (default) and vector similarity (when embeddings available).
"""

import json
import sys
import os
import argparse
from typing import List, Dict, Tuple

MEMORY_DIR = ".antigravity/state"
ARCHIVE_FILE = os.path.join(MEMORY_DIR, "archived_memory.json")
ACTIVE_FILE = os.path.join(MEMORY_DIR, "memory.json")
EMBEDDINGS_FILE = os.path.join(MEMORY_DIR, "embeddings.faiss")

# Optional imports for vector search
VECTOR_SEARCH_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    pass

def load_memory(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return data.get('learnings', [])
    except json.JSONDecodeError:
        return []

def keyword_search(query: str, learnings: List[Dict], limit: int) -> List[Tuple[int, Dict]]:
    """Simple keyword-based search."""
    query_terms = query.lower().split()
    results = []
    
    for item in learnings:
        if not isinstance(item, dict): 
            continue
        text = str(item.get('pattern', '')) + " " + str(item.get('resolution', '')) + " " + str(item.get('category', ''))
        text_lower = text.lower()
        score = sum(1 for term in query_terms if term in text_lower)
        if score > 0:
            results.append((score, item))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:limit]

def vector_search(query: str, learnings: List[Dict], limit: int) -> List[Tuple[float, Dict]]:
    """Vector similarity search using sentence-transformers."""
    if not VECTOR_SEARCH_AVAILABLE:
        return []
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])[0]
    
    results = []
    for item in learnings:
        if not isinstance(item, dict):
            continue
        text = str(item.get('pattern', '')) + " " + str(item.get('resolution', ''))
        item_embedding = model.encode([text])[0]
        
        # Cosine similarity
        similarity = np.dot(query_embedding, item_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(item_embedding))
        results.append((float(similarity), item))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:limit]

def search_memory(query: str, limit: int = 5, use_vector: bool = False) -> None:
    """Search both active and archived memory for learnings matching the query."""
    active_learnings = load_memory(ACTIVE_FILE)
    archived_learnings = load_memory(ARCHIVE_FILE)
    all_learnings = active_learnings + archived_learnings
    
    if use_vector and VECTOR_SEARCH_AVAILABLE:
        print("🔍 Using Vector Search (semantic matching)")
        results = vector_search(query, all_learnings, limit)
        score_label = "Similarity"
    else:
        if use_vector and not VECTOR_SEARCH_AVAILABLE:
            print("⚠️ Vector search requested but sentence-transformers not installed. Falling back to keyword search.")
        print("🔍 Using Keyword Search")
        results = keyword_search(query, all_learnings, limit)
        score_label = "Score"
    
    print(f"=== Memory Search Results for '{query}' ===")
    print(f"Found {len(results)} matches. Showing top {limit}.\n")
    
    for i, (score, item) in enumerate(results, 1):
        score_display = f"{score:.2f}" if isinstance(score, float) else str(score)
        print(f"{i}. [{score_label}: {score_display}] {item.get('id', 'N/A')} ({item.get('category', 'General')})")
        print(f"   Pattern: {item.get('pattern', 'N/A')}")
        print(f"   Resolution: {item.get('resolution', 'N/A')}")
        print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search Agent Memory")
    parser.add_argument("query", help="Search keywords (e.g. 'terraform lock state')")
    parser.add_argument("--limit", type=int, default=5, help="Max results to return")
    parser.add_argument("--vector", action="store_true", help="Use vector search (requires sentence-transformers)")
    
    args = parser.parse_args()
    search_memory(args.query, args.limit, args.vector)
