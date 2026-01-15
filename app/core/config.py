from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    MCP_SERVER_NAME: str = "pdf-splitter-mcp"
    PROJECT_NAME: str = "PDF Splitter MCP"
    VERSION: str = "0.1.0"
    # Use local relative path for dev
    TEMP_DIRECTORY: Path = Path("data/temp")
    DEBUG: bool = True
    # CORS origins for the FastAPI app
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
# Ensure dir exists
settings.TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)
