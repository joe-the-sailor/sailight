"""
Utility-Funktionen für die Frontend-Anwendung
"""

from .api_client import APIClient, api_client
from .auth import AuthManager, auth_manager
from .theme import apply_theme, get_theme_stylesheet
from .helpers import (
    format_date, format_datetime, format_number, format_currency,
    truncate_text, generate_id, validate_email, validate_phone
)
from .file_utils import save_file, open_file, get_file_info
from .logging import setup_logging, get_logger

__all__ = [
    'APIClient', 'api_client',
    'AuthManager', 'auth_manager',
    'apply_theme', 'get_theme_stylesheet',
    'format_date', 'format_datetime', 'format_number', 'format_currency',
    'truncate_text', 'generate_id', 'validate_email', 'validate_phone',
    'save_file', 'open_file', 'get_file_info',
    'setup_logging', 'get_logger'
]
