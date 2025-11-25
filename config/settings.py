"""
Configuration management for CircularQuery.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_API_BASE = "https://slack.com/api"
    
    # LLM Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite4")
    
    # Database Configuration
    SQLITE_PATH = os.getenv("SQLITE_PATH", "./chinook.db")
    SCHEMA_YAML_PATH = os.getenv("SCHEMA_YAML_PATH", "./schema.yaml")
    
    # Application Configuration
    EXPORTS_DIR = "./exports"
    ROWS_PER_PAGE = 12
    DEFAULT_LIMIT = 500
    LLM_TIMEOUT = 120
    
    # Optional Configuration
    NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN", "")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.SLACK_BOT_TOKEN:
            raise ValueError("SLACK_BOT_TOKEN is required")
        
        if not os.path.exists(cls.SQLITE_PATH):
            raise FileNotFoundError(f"SQLite database not found at {cls.SQLITE_PATH}")
        
        # Create exports directory if it doesn't exist
        os.makedirs(cls.EXPORTS_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Default configuration
config = DevelopmentConfig()