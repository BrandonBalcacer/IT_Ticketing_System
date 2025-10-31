# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class - stores all settings for the application
    Uses environment variables to keep sensitive data secure
    """
    
    # Secret key for session management (used to encrypt session data)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # For development, we use SQLite (a simple file-based database)
    # For production, we'll use PostgreSQL on AWS RDS
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ticketing_system.db'
    
    # Disable SQLAlchemy event system (not needed, saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS configuration - allows frontend to communicate with backend
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """
    Development-specific configuration
    Used when building and testing locally
    """
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """
    Production-specific configuration
    Used when deployed to AWS
    """
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """
    Testing-specific configuration
    Used when running automated tests
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_ticketing_system.db'


# Dictionary to easily select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}