from dataclasses import dataclass
from dotenv import load_dotenv
import os

@dataclass(frozen=True)
class AppConfig:
    api_key_llm: str | None
    db_url: str | None
    db_type: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    db_normalize_embeddings: bool
    device: str
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        load_dotenv()  
        return cls(
            api_key_llm=os.getenv("API_KEY_LLM"),
            db_url=os.getenv("DB_URL"),
            db_type=(os.getenv("DB_TYPE", "") or "").lower().strip(),
            db_user=os.getenv("DB_USER", "") or "",
            db_password=os.getenv("DB_PASSWORD", "") or "",
            db_host=os.getenv("DB_HOST", "localhost") or "localhost",
            db_port=os.getenv("DB_PORT", "") or "",
            db_name=os.getenv("DB_NAME", "") or "",
            db_normalize_embeddings=os.getenv("DB_NORMALIZE_EMBEDDINGS", "True") or 'True',
            device=os.getenv("DEVICE", "cpu") or "cpu",
        )
