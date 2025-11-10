#!/usr/bin/env python3
# Save secrets into the OS keyring (safer than storing in files).
# Usage: python scripts/save_keyring.py
import getpass
import keyring
from typing import List

SERVICE = "universal-ai-orchestrator"
KEYS: List[str] = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "NOTION_API_KEY",
    "NOTION_DATABASE_ID",
]

def set_secret(name: str):
    val = getpass.getpass(f"Enter value for {name} (leave blank to skip): ")
    if val:
        keyring.set_password(SERVICE, name, val)
        print(f"{name} stored in OS keyring.")

def get_secret(name: str):
    return keyring.get_password(SERVICE, name)

if __name__ == "__main__":
    try:
        import keyring
    except Exception:
        print("Please install keyring: pip install keyring")
        raise SystemExit(1)

    for key in KEYS:
        set_secret(key)

    print("Secrets stored in OS keyring. Use keyring.get_password(SERVICE, NAME) in your code to retrieve them.")