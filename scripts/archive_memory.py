#!/usr/bin/env python3
"""
Memory Archiver
Moves older learnings from `memory.json` to `archived_memory.json` to keep active context small.
"""

import json
import sys
import os
import shutil
from datetime import datetime, timezone

MEMORY_DIR = ".antigravity/state"
ACTIVE_FILE = os.path.join(MEMORY_DIR, "memory.json")
ARCHIVE_FILE = os.path.join(MEMORY_DIR, "archived_memory.json")
MAX_ACTIVE_LEARNINGS = 10  # Keep only the last 10 learnings in active context

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_json(filepath, data):
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def archive_memory():
    active_data = load_json(ACTIVE_FILE)
    if not active_data or 'learnings' not in active_data:
        print("No active learnings to archive.")
        return

    learnings = active_data.get('learnings', [])
    
    if len(learnings) <= MAX_ACTIVE_LEARNINGS:
        print(f"Active learnings ({len(learnings)}) are within limit ({MAX_ACTIVE_LEARNINGS}). No archiving needed.")
        return

    # Split learnings
    # Newest at the end usually, so we keep the last N
    # Assuming append-only, so last items are newest
    items_to_keep = learnings[-MAX_ACTIVE_LEARNINGS:]
    items_to_archive = learnings[:-MAX_ACTIVE_LEARNINGS]

    # Load archive
    archive_data = load_json(ARCHIVE_FILE)
    archived_list = archive_data.get('learnings', [])
    
    # Append new archived items
    archived_list.extend(items_to_archive)
    
    # Update structures
    active_data['learnings'] = items_to_keep
    
    # Update archive structure
    if 'learnings' not in archive_data:
        archive_data = {'version': '1.0', 'last_updated': datetime.now(timezone.utc).isoformat(), 'learnings': []}
        archived_list = items_to_archive # Re-assign if new
    
    archive_data['learnings'] = archived_list
    archive_data['last_updated'] = datetime.now(timezone.utc).isoformat()

    # Save both
    save_json(ACTIVE_FILE, active_data)
    save_json(ARCHIVE_FILE, archive_data)
    
    print(f"✅ Archived {len(items_to_archive)} items. Active memory now has {len(items_to_keep)} items.")

if __name__ == "__main__":
    archive_memory()
