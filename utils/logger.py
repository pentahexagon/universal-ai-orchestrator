"""
Logging configuration
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def get_logger(
    name: str, level: str = "INFO", log_file: Optional[str] = "logs/orchestrator.log"
) -> logging.Logger:
    """
    구조화된 로거 생성

    Args:
        name: 로거 이름 (__name__ 사용 권장)
        level: 로그 레벨 (DEBUG|INFO|WARNING|ERROR)
        log_file: 로그 파일 경로

    Returns:
        설정된 Logger 객체
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 재사용
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # 포맷터
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (로테이션)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
