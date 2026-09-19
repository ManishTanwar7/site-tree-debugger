"""
Simple, reliable file-based JSON storage for audit history and user settings.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "audits_history.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_settings() -> Dict[str, Any]:
    _ensure_data_dir()
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "gemini_api_key": "",
        "preferred_model": "gemini-2.5-flash",
        "deep_scan": True
    }

def save_settings(settings: Dict[str, Any]) -> None:
    _ensure_data_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def save_audit_record(record: Dict[str, Any]) -> str:
    _ensure_data_dir()
    history = get_all_audits()
    
    audit_id = f"audit_{int(time.time())}_{len(history)+1}"
    record["id"] = audit_id
    record["timestamp"] = int(time.time())
    
    # Prepend newest
    history.insert(0, record)
    
    # Keep last 50 audits
    history = history[:50]
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)
        
    return audit_id

def get_all_audits() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def get_audit_by_id(audit_id: str) -> Optional[Dict[str, Any]]:
    audits = get_all_audits()
    for a in audits:
        if a.get("id") == audit_id:
            return a
    return None
