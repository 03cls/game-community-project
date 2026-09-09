"""应用配置：从 .env 读取，提供合理默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载 .env（开发默认 SQLite，零配置可跑）
load_dotenv(BASE_DIR / ".env")

# 数据目录（SQLite 文件落点）
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    """全局配置单例（简单 dict-like，避免 pydantic-settings 额外依赖）。"""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'game_community.db'}",
    )
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "game-community-dev-secret-change-me")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
    JWT_ALGORITHM: str = "HS256"

    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # 本地 Ollama 大模型（轻量中文模型 qwen2.5:3b），优先于 DeepSeek
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    OLLAMA_ENABLED: str = os.getenv("OLLAMA_ENABLED", "1")  # 默认开启本地 Ollama

    @property
    def ollama_enabled(self) -> bool:
        return self.OLLAMA_ENABLED == "1"

    @property
    def ai_enabled(self) -> bool:
        # 本地 Ollama 或 DeepSeek 任一可用即视为 AI 已启用
        return self.ollama_enabled or bool(self.DEEPSEEK_API_KEY)


settings = Settings()
