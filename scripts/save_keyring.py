#!/usr/bin/env python3
"""
OS 키링에 API 키를 안전하게 저장하는 스크립트
사용법: python scripts/save_keyring.py

필요 패키지: pip install keyring
"""

import keyring
import getpass

SERVICE_NAME = "universal-ai-orchestrator"

def save_secret(key_name: str, prompt: str):
    """대화형으로 시크릿 입력받아 키링에 저장"""
    value = getpass.getpass(f"{prompt} (leave blank to skip): ")
    if value.strip():
        keyring.set_password(SERVICE_NAME, key_name, value)
        print(f"✓ {key_name} saved to OS keyring")
    else:
        print(f"⊘ {key_name} skipped")

def main():
    print("Saving secrets to OS keyring...")
    print(f"Service name: {SERVICE_NAME}\n")

    save_secret("OPENAI_API_KEY", "Set OPENAI_API_KEY")
    save_secret("ANTHROPIC_API_KEY", "Set ANTHROPIC_API_KEY")
    save_secret("GEMINI_API_KEY", "Set GEMINI_API_KEY")
    save_secret("NOTION_API_KEY", "Set NOTION_API_KEY")
    save_secret("NOTION_DATABASE_ID", "Set NOTION_DATABASE_ID")

    print("\n✅ Secrets saved to OS keyring")
    print(f"To retrieve: keyring.get_password('{SERVICE_NAME}', 'KEY_NAME')")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure 'keyring' is installed: pip install keyring")
