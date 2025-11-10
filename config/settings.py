"""
Configuration Manager
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)

# Optional keyring support
try:
    import keyring

    KEYRING_AVAILABLE = True
    KEYRING_SERVICE = "universal-ai-orchestrator"
except ImportError:
    KEYRING_AVAILABLE = False
    KEYRING_SERVICE = None


class ConfigManager:
    """
    YAML 설정 + 환경변수 통합 관리
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: YAML 설정 파일 경로
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._load_env_vars()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """YAML 파일 로드"""
        if not self.config_path.exists():
            logger.warning(f"설정 파일 없음: {self.config_path}, 기본값 사용")
            return self._get_default_config()

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_secret(self, key_name: str) -> Optional[str]:
        """
        시크릿 가져오기 (우선순위: 환경변수 > keyring > None)

        Args:
            key_name: 시크릿 키 이름

        Returns:
            시크릿 값 또는 None
        """
        # 1. 환경변수에서 먼저 확인
        value = os.getenv(key_name)
        if value:
            return value

        # 2. keyring에서 fallback (설치되어 있으면)
        if KEYRING_AVAILABLE:
            try:
                value = keyring.get_password(KEYRING_SERVICE, key_name)
                if value:
                    logger.debug(f"Loaded {key_name} from keyring")
                    return value
            except Exception as e:
                logger.debug(f"Keyring lookup failed for {key_name}: {e}")

        return None

    def _load_env_vars(self):
        """환경변수 로드 (.env 파일 및 keyring)"""
        load_dotenv()

        # API 키는 환경변수 또는 keyring에서 로드 (보안)
        self.config["api_keys"] = {
            "anthropic": self._get_secret("ANTHROPIC_API_KEY"),
            "openai": self._get_secret("OPENAI_API_KEY"),
            "gemini": self._get_secret("GEMINI_API_KEY"),
            "notion": self._get_secret("NOTION_API_KEY"),
        }

        self.config["notion_db_ids"] = {
            "inbox": self._get_secret("NOTION_INBOX_DB_ID"),
            "results": self._get_secret("NOTION_RESULTS_DB_ID"),
        }

    def _validate_config(self):
        """설정 검증"""
        required_keys = [
            "api_keys.anthropic",
            "api_keys.openai",
            "api_keys.gemini",
            "api_keys.notion",
            "notion_db_ids.inbox",
            "notion_db_ids.results",
        ]

        missing = []
        for key in required_keys:
            if not self._get_nested(self.config, key):
                missing.append(key)

        if missing:
            raise ValueError(
                f"❌ 필수 설정 누락: {', '.join(missing)}\n"
                f"📝 .env 파일을 확인하세요"
            )

        logger.info("✅ 설정 검증 완료")

    def _get_nested(self, d: dict, path: str):
        """중첩된 딕셔너리 값 가져오기"""
        keys = path.split(".")
        for key in keys:
            d = d.get(key, {})
            if not d:
                return None
        return d

    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정"""
        return {
            "system": {
                "polling_interval": 30,
                "max_concurrent_tasks": 5,
                "log_level": "INFO",
            },
            "agents": {
                "gemini": {"model": "gemini-pro", "timeout": 120, "max_retries": 3},
                "chatgpt": {
                    "model": "gpt-4",
                    "timeout": 120,
                    "max_retries": 3,
                    "temperature": 0.7,
                },
                "claude": {
                    "model": "claude-sonnet-4-5-20250929",
                    "timeout": 120,
                    "max_retries": 3,
                },
            },
            "rate_limits": {
                "gemini": {"max_requests": 60, "time_window": 60},
                "openai": {"max_requests": 50, "time_window": 60},
                "anthropic": {"max_requests": 50, "time_window": 60},
                "notion": {"max_requests": 3, "time_window": 1},
            },
        }

    def get(self, key: str, default=None):
        """설정 값 가져오기"""
        return self._get_nested(self.config, key) or default

    def __getitem__(self, key: str):
        """딕셔너리 스타일 접근"""
        return self.config[key]
