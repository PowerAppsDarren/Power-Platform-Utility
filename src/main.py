#!/usr/bin/env python3
"""
Power Platform Utility - Main Application Entry Point

A PySide6-based GUI application for interfacing with Power Platform environments
using the PAC CLI (Power Platform CLI).

Author: GitHub Copilot Assistant
License: MIT
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from utils.helpers import setup_logging, load_config


def main():
    """Main application entry point."""
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Power Platform Utility...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Power Platform Utility")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Power Platform Tools")
    
    # Set application properties
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    # Load configuration
    config = load_config()
    
    # Create and show main window
    main_window = MainWindow(config)
    main_window.show()
    
    logger.info("Application started successfully")
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
