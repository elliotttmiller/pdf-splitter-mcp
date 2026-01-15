from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    MCP_SERVER_NAME: str = "pdf-splitter-mcp"
    # Use local relative path for dev
    TEMP_DIRECTORY: Path = Path("data/temp")
    
    class Config:
        env_file = ".env"

settings = Settings()
# Ensure dir exists
settings.TEMP_DIRECTORY.mkdir(parents=True, exist_ok=True)
