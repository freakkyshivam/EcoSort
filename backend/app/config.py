from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = the ecosort-backend/ folder (2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    All configurable values live here. Anything can be overridden by
    setting an environment variable of the same name (case-insensitive),
    or by putting it in a .env file at the project root.

    Example .env:
        DATABASE_URL=sqlite:///./ecosort.db
        MODEL_CHECKPOINT_PATH=ml/outputs/ecosort_convnext_tiny_best.pt
    """

    # --- Database ---
    # SQLite for now. Later, just change this to your Neon connection string,
    # e.g. postgresql://user:pass@host/dbname — no other code changes needed.
    database_url: str = f"sqlite:///{BASE_DIR / 'ecosort.db'}"

    # --- ML model ---
    model_checkpoint_path: Path = BASE_DIR / "ml" / "outputs" / "ecosort_convnext_tiny_best.pt"
    confidence_threshold: float = 0.70

    # --- API ---
    api_v1_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Import this single instance everywhere you need a setting:
#   from app.config import settings
#   settings.database_url
settings = Settings()