"""
Utility Helper Functions

This module contains utility functions used throughout the application.
"""

import os
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up application logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_path = Path(log_file)
    else:
        file_path = log_dir / "power_platform_utility.log"
    
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load application configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing configuration settings
    """
    
    if config_path is None:
        config_path = Path("config") / "settings.json"
    else:
        config_path = Path(config_path)
    
    # Default configuration
    default_config = {
        "application": {
            "name": "Power Platform Utility",
            "version": "1.0.0",
            "theme": "default"
        },
        "pac_cli": {
            "timeout": 30,
            "retry_attempts": 3
        },
        "ui": {
            "window_width": 1200,
            "window_height": 800,
            "remember_size": True,
            "remember_position": True
        },
        "logging": {
            "level": "INFO",
            "file_logging": True
        }
    }
    
    # Load configuration from file if it exists
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                # Merge with default config
                default_config.update(file_config)
        except (json.JSONDecodeError, IOError) as e:
            logging.warning(f"Failed to load config file {config_path}: {e}")
    
    return default_config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    Save application configuration to JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to configuration file
        
    Returns:
        True if successful, False otherwise
    """
    
    if config_path is None:
        config_path = Path("config") / "settings.json"
    else:
        config_path = Path(config_path)
    
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        logging.error(f"Failed to save config file {config_path}: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path is valid and accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid, False otherwise
    """
    
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_directory_path(dir_path: str) -> bool:
    """
    Validate if a directory path is valid and accessible.
    
    Args:
        dir_path: Directory path to validate
        
    Returns:
        True if valid, False otherwise
    """
    
    try:
        path = Path(dir_path)
        return path.exists() and path.is_dir()
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    
    # Characters not allowed in Windows filenames
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename


def get_app_data_dir() -> Path:
    """
    Get the application data directory.
    
    Returns:
        Path to application data directory
    """
    
    if os.name == 'nt':  # Windows
        app_data = os.environ.get('APPDATA', '')
        return Path(app_data) / "PowerPlatformUtility"
    else:  # Unix-like systems
        home = os.environ.get('HOME', '')
        return Path(home) / ".power_platform_utility"
