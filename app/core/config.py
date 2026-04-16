from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

load_dotenv()


# =========================
# ✅ ENV SETTINGS
# =========================

class Settings(BaseSettings):
    GROQ_API_KEY: str
    API_TITLE: str = "HealthRx AI"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # CSV path (string for compatibility)
    SYMPTOMS_CSV: str = str(BASE_DIR / "data" / "symptoms.csv")

    # ML config
    N_ESTIMATORS: int = 50
    MAX_DEPTH: Optional[int] = None
    MIN_SAMPLES_SPLIT: int = 2
    MIN_SAMPLES_LEAF: int = 1
    RANDOM_STATE: int = 42

    class Config:
        env_file = ".env"
        extra = "ignore"  # prevents crash if extra env vars exist


settings = Settings()


# =========================
# ✅ APP CONFIG
# =========================

@dataclass(frozen=True)
class AppConfig:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = field(default_factory=lambda: Path("data"))


app_config = AppConfig()