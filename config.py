"""
Application Configuration Module
Supports Development, Testing, and Production environments.
Reads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / '.env')

# Default SQLite database path inside the instance/ folder for persistent storage
DEFAULT_DB_DIR = BASE_DIR / 'instance'
DEFAULT_DB_PATH = DEFAULT_DB_DIR / 'tasks.db'


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'taskmanager-dev-secret-key-change-in-prod-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

    # Database configuration
    # Use DATABASE_URL if provided (e.g. from Docker/ECS/Kubernetes/EC2),
    # otherwise fallback to local SQLite database in instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Ensure instance directory exists for SQLite storage
        DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration (uses in-memory database)."""
    DEBUG = False
    TESTING = True
    # Isolated in-memory database so production or development data is never affected
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # In production, ensure a strong secret key is supplied
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-production-key-must-be-set')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
