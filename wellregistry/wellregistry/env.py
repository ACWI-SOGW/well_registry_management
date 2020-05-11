"""
Environment values convenience class.
"""
import os


class Environment:
    """Environment or context variables or parameters."""

    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'postgres')
    APP_DATABASE_NAME = os.getenv('APP_DATABASE_NAME')
    APP_DATABASE_HOST = os.getenv('APP_DATABASE_HOST')
    APP_DATABASE_PORT = os.getenv('APP_DATABASE_PORT', default='5432')
    APP_DB_OWNER_USERNAME = os.getenv('APP_DB_OWNER_USERNAME')
    APP_DB_OWNER_PASSWORD = os.getenv('APP_DB_OWNER_PASSWORD')
    APP_SCHEMA = os.getenv('APP_SCHEMA')
    APP_SCHEMA_OWNER_USERNAME = os.getenv('APP_SCHEMA_OWNER_USERNAME')
    APP_SCHEMA_OWNER_PASSWORD = os.getenv('APP_SCHEMA_OWNER_PASSWORD')
    APP_ADMIN_USERNAME = os.getenv('APP_ADMIN_USERNAME')
    APP_ADMIN_PASSWORD = os.getenv('APP_ADMIN_PASSWORD')
    APP_CLIENT_USERNAME = os.getenv('APP_CLIENT_USERNAME')
    APP_CLIENT_PASSWORD = os.getenv('APP_CLIENT_PASSWORD')
