"""
Main Application Window

This module contains the main window class for the Power Platform Utility application.
"""

import logging
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QStatusBar, QToolBar, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit, QSplitter, QGroupBox,
    QProgressBar, QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QFont, QPixmap

from core.pac_cli import PACCLIWrapper, PACCLIError
from core.environment import EnvironmentManager, PowerPlatformEnvironment


class WorkerThread(QThread):
    """Background worker thread for long-running operations."""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, operation, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.operation(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize core components
        try:
            self.pac_cli = PACCLIWrapper()
            self.environment_manager = EnvironmentManager(self.pac_cli)
        except PACCLIError as e:
            QMessageBox.critical(self, "PAC CLI Error", str(e))
            sys.exit(1)
        
        # UI Components
        self.central_widget = None
        self.tab_widget = None
        self.environment_combo = None
        self.status_label = None
        self.progress_bar = None
        self.log_text = None
        
        # Current state
        self.current_environment = None
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_tool_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Load initial data
        self.refresh_environments()
        
        self.logger.info("Main window initialized")
    
    def setup_ui(self):
        """Set up the main user interface."""
        
        # Set window properties
        self.setWindowTitle("Power Platform Utility")
        self.setMinimumSize(1000, 700)
        
        # Apply window size from config
        width = self.config.get("ui", {}).get("window_width", 1200)
        height = self.config.get("ui", {}).get("window_height", 800)
        self.resize(width, height)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        
        # Environment selection section
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QHBoxLayout(env_frame)
        
        env_layout.addWidget(QLabel("Environment:"))
        self.environment_combo = QComboBox()
        self.environment_combo.setMinimumWidth(300)
        env_layout.addWidget(self.environment_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_environments)
        env_layout.addWidget(refresh_btn)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_to_environment)
        env_layout.addWidget(connect_btn)
        
        env_layout.addStretch()
        
        main_layout.addWidget(env_frame)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_overview_tab()
        self.create_solutions_tab()
        self.create_import_export_tab()
        self.create_logs_tab()
        
        # Log section at bottom
        log_splitter = QSplitter(Qt.Vertical)
        log_splitter.addWidget(self.tab_widget)
        
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_splitter.addWidget(log_group)
        log_splitter.setStretchFactor(0, 1)
        log_splitter.setStretchFactor(1, 0)
        
        main_layout.addWidget(log_splitter)
    
    def create_overview_tab(self):
        """Create the overview tab."""
        
        overview_widget = QWidget()
        layout = QVBoxLayout(overview_widget)
        
        # Environment info
        env_group = QGroupBox("Current Environment")
        env_layout = QFormLayout(env_group)
        
        self.env_name_label = QLabel("Not connected")
        self.env_url_label = QLabel("Not connected")
        self.env_region_label = QLabel("Not connected")
        self.env_type_label = QLabel("Not connected")
        
        env_layout.addRow("Name:", self.env_name_label)
        env_layout.addRow("URL:", self.env_url_label)
        env_layout.addRow("Region:", self.env_region_label)
        env_layout.addRow("Type:", self.env_type_label)
        
        layout.addWidget(env_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        auth_btn = QPushButton("Authenticate")
        auth_btn.clicked.connect(self.authenticate)
        actions_layout.addWidget(auth_btn)
        
        list_solutions_btn = QPushButton("List Solutions")
        list_solutions_btn.clicked.connect(self.list_solutions)
        actions_layout.addWidget(list_solutions_btn)
        
        layout.addWidget(actions_group)
        layout.addStretch()
        
        self.tab_widget.addTab(overview_widget, "Overview")
    
    def create_solutions_tab(self):
        """Create the solutions management tab."""
        
        solutions_widget = QWidget()
        layout = QVBoxLayout(solutions_widget)
        
        # Solutions table
        self.solutions_table = QTableWidget()
        self.solutions_table.setColumnCount(4)
        self.solutions_table.setHorizontalHeaderLabels(["Name", "Display Name", "Version", "Managed"])
        layout.addWidget(self.solutions_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_solutions_btn = QPushButton("Refresh")
        refresh_solutions_btn.clicked.connect(self.list_solutions)
        button_layout.addWidget(refresh_solutions_btn)
        
        export_btn = QPushButton("Export Selected")
        export_btn.clicked.connect(self.export_solution)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(solutions_widget, "Solutions")
    
    def create_import_export_tab(self):
        """Create the import/export tab."""
        
        import_export_widget = QWidget()
        layout = QVBoxLayout(import_export_widget)
        
        # Import section
        import_group = QGroupBox("Import Solution")
        import_layout = QFormLayout(import_group)
        
        self.import_path_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_import_file)
        
        import_path_layout = QHBoxLayout()
        import_path_layout.addWidget(self.import_path_edit)
        import_path_layout.addWidget(browse_btn)
        
        import_layout.addRow("Solution File:", import_path_layout)
        
        self.publish_workflows_check = QCheckBox("Publish Workflows")
        self.publish_workflows_check.setChecked(True)
        import_layout.addRow("Options:", self.publish_workflows_check)
        
        import_btn = QPushButton("Import Solution")
        import_btn.clicked.connect(self.import_solution)
        import_layout.addRow(import_btn)
        
        layout.addWidget(import_group)
        
        # Export section
        export_group = QGroupBox("Export Solution")
        export_layout = QFormLayout(export_group)
        
        self.export_solution_combo = QComboBox()
        export_layout.addRow("Solution:", self.export_solution_combo)
        
        self.export_path_edit = QLineEdit()
        export_browse_btn = QPushButton("Browse...")
        export_browse_btn.clicked.connect(self.browse_export_folder)
        
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(self.export_path_edit)
        export_path_layout.addWidget(export_browse_btn)
        
        export_layout.addRow("Export Path:", export_path_layout)
        
        self.managed_export_check = QCheckBox("Export as Managed")
        export_layout.addRow("Options:", self.managed_export_check)
        
        export_btn = QPushButton("Export Solution")
        export_btn.clicked.connect(self.export_solution)
        export_layout.addRow(export_btn)
        
        layout.addWidget(export_group)
        layout.addStretch()
        
        self.tab_widget.addTab(import_export_widget, "Import/Export")
    
    def create_logs_tab(self):
        """Create the logs tab."""
        
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)
        
        self.detailed_log_text = QTextEdit()
        self.detailed_log_text.setReadOnly(True)
        self.detailed_log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.detailed_log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        log_controls.addWidget(clear_btn)
        
        save_btn = QPushButton("Save Logs")
        save_btn.clicked.connect(self.save_logs)
        log_controls.addWidget(save_btn)
        
        log_controls.addStretch()
        layout.addLayout(log_controls)
        
        self.tab_widget.addTab(logs_widget, "Logs")
    
    def setup_menu_bar(self):
        """Set up the menu bar."""
        
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        refresh_action = QAction("Refresh Environments", self)
        refresh_action.triggered.connect(self.refresh_environments)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        auth_action = QAction("Authenticate", self)
        auth_action.triggered.connect(self.authenticate)
        tools_menu.addAction(auth_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tool_bar(self):
        """Set up the tool bar."""
        
        toolbar = self.addToolBar("Main")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_environments)
        toolbar.addAction(refresh_action)
        
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.connect_to_environment)
        toolbar.addAction(connect_action)
        
        toolbar.addSeparator()
        
        auth_action = QAction("Authenticate", self)
        auth_action.triggered.connect(self.authenticate)
        toolbar.addAction(auth_action)
    
    def setup_status_bar(self):
        """Set up the status bar."""
        
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
    
    def setup_connections(self):
        """Set up signal connections."""
        
        self.environment_combo.currentTextChanged.connect(self.on_environment_changed)
    
    def log_message(self, message: str):
        """Add a message to the log displays."""
        
        self.log_text.append(message)
        self.detailed_log_text.append(message)
        
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        self.detailed_log_text.verticalScrollBar().setValue(
            self.detailed_log_text.verticalScrollBar().maximum()
        )
    
    def set_status(self, message: str):
        """Set the status bar message."""
        
        self.status_label.setText(message)
        self.log_message(f"Status: {message}")
    
    def show_progress(self, show: bool = True):
        """Show or hide the progress bar."""
        
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
    
    def refresh_environments(self):
        """Refresh the list of environments."""
        
        self.set_status("Refreshing environments...")
        self.show_progress(True)
        
        def refresh_worker():
            return self.environment_manager.refresh_environments()
        
        self.worker = WorkerThread(refresh_worker)
        self.worker.finished.connect(self.on_environments_refreshed)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_environments_refreshed(self, success: bool):
        """Handle environments refresh completion."""
        
        self.show_progress(False)
        
        if success:
            self.environment_combo.clear()
            environments = self.environment_manager.get_environments()
            
            for env in environments:
                self.environment_combo.addItem(env.display_name, env)
            
            self.set_status(f"Found {len(environments)} environments")
        else:
            self.set_status("Failed to refresh environments")
            QMessageBox.warning(self, "Warning", "Failed to refresh environments")
    
    def on_environment_changed(self, text: str):
        """Handle environment selection change."""
        
        current_data = self.environment_combo.currentData()
        if isinstance(current_data, PowerPlatformEnvironment):
            self.current_environment = current_data
    
    def connect_to_environment(self):
        """Connect to the selected environment."""
        
        if not self.current_environment:
            QMessageBox.warning(self, "Warning", "Please select an environment first")
            return
        
        self.set_status(f"Connecting to {self.current_environment.display_name}...")
        self.show_progress(True)
        
        def connect_worker():
            return self.environment_manager.select_environment(self.current_environment)
        
        self.worker = WorkerThread(connect_worker)
        self.worker.finished.connect(self.on_environment_connected)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_environment_connected(self, success: bool):
        """Handle environment connection completion."""
        
        self.show_progress(False)
        
        if success:
            self.set_status(f"Connected to {self.current_environment.display_name}")
            self.update_environment_info()
        else:
            self.set_status("Failed to connect to environment")
            QMessageBox.warning(self, "Warning", "Failed to connect to environment")
    
    def update_environment_info(self):
        """Update the environment information display."""
        
        if self.current_environment:
            self.env_name_label.setText(self.current_environment.name)
            self.env_url_label.setText(self.current_environment.url)
            self.env_region_label.setText(self.current_environment.region)
            self.env_type_label.setText(self.current_environment.environment_type)
    
    def authenticate(self):
        """Authenticate with Power Platform."""
        
        self.set_status("Authenticating...")
        self.show_progress(True)
        
        def auth_worker():
            return self.pac_cli.authenticate()
        
        self.worker = WorkerThread(auth_worker)
        self.worker.finished.connect(self.on_authentication_complete)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_authentication_complete(self, success: bool):
        """Handle authentication completion."""
        
        self.show_progress(False)
        
        if success:
            self.set_status("Authentication successful")
            QMessageBox.information(self, "Success", "Authentication successful")
        else:
            self.set_status("Authentication failed")
            QMessageBox.warning(self, "Warning", "Authentication failed")
    
    def list_solutions(self):
        """List solutions in the current environment."""
        
        if not self.current_environment:
            QMessageBox.warning(self, "Warning", "Please connect to an environment first")
            return
        
        self.set_status("Loading solutions...")
        self.show_progress(True)
        
        def solutions_worker():
            return self.pac_cli.get_solutions()
        
        self.worker = WorkerThread(solutions_worker)
        self.worker.finished.connect(self.on_solutions_loaded)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_solutions_loaded(self, solutions: List[Dict[str, Any]]):
        """Handle solutions list completion."""
        
        self.show_progress(False)
        
        self.solutions_table.setRowCount(len(solutions))
        self.export_solution_combo.clear()
        
        for i, solution in enumerate(solutions):
            self.solutions_table.setItem(i, 0, QTableWidgetItem(solution.get('UniqueName', '')))
            self.solutions_table.setItem(i, 1, QTableWidgetItem(solution.get('FriendlyName', '')))
            self.solutions_table.setItem(i, 2, QTableWidgetItem(solution.get('Version', '')))
            self.solutions_table.setItem(i, 3, QTableWidgetItem(str(solution.get('IsManaged', False))))
            
            # Add to export combo
            self.export_solution_combo.addItem(solution.get('FriendlyName', ''), solution.get('UniqueName', ''))
        
        self.set_status(f"Loaded {len(solutions)} solutions")
    
    def browse_import_file(self):
        """Browse for import file."""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Solution File",
            "",
            "Solution Files (*.zip);;All Files (*)"
        )
        
        if file_path:
            self.import_path_edit.setText(file_path)
    
    def browse_export_folder(self):
        """Browse for export folder."""
        
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Export Folder"
        )
        
        if folder_path:
            self.export_path_edit.setText(folder_path)
    
    def import_solution(self):
        """Import a solution."""
        
        file_path = self.import_path_edit.text()
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please select a solution file")
            return
        
        if not self.current_environment:
            QMessageBox.warning(self, "Warning", "Please connect to an environment first")
            return
        
        self.set_status("Importing solution...")
        self.show_progress(True)
        
        def import_worker():
            return self.pac_cli.import_solution(file_path, self.publish_workflows_check.isChecked())
        
        self.worker = WorkerThread(import_worker)
        self.worker.finished.connect(self.on_import_complete)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_import_complete(self, success: bool):
        """Handle import completion."""
        
        self.show_progress(False)
        
        if success:
            self.set_status("Solution imported successfully")
            QMessageBox.information(self, "Success", "Solution imported successfully")
        else:
            self.set_status("Solution import failed")
            QMessageBox.warning(self, "Warning", "Solution import failed")
    
    def export_solution(self):
        """Export a solution."""
        
        solution_name = self.export_solution_combo.currentData()
        export_path = self.export_path_edit.text()
        
        if not solution_name:
            QMessageBox.warning(self, "Warning", "Please select a solution to export")
            return
        
        if not export_path:
            QMessageBox.warning(self, "Warning", "Please select an export folder")
            return
        
        if not self.current_environment:
            QMessageBox.warning(self, "Warning", "Please connect to an environment first")
            return
        
        self.set_status("Exporting solution...")
        self.show_progress(True)
        
        def export_worker():
            return self.pac_cli.export_solution(solution_name, export_path, self.managed_export_check.isChecked())
        
        self.worker = WorkerThread(export_worker)
        self.worker.finished.connect(self.on_export_complete)
        self.worker.error.connect(self.on_worker_error)
        self.worker.start()
    
    def on_export_complete(self, success: bool):
        """Handle export completion."""
        
        self.show_progress(False)
        
        if success:
            self.set_status("Solution exported successfully")
            QMessageBox.information(self, "Success", "Solution exported successfully")
        else:
            self.set_status("Solution export failed")
            QMessageBox.warning(self, "Warning", "Solution export failed")
    
    def on_worker_error(self, error_message: str):
        """Handle worker thread errors."""
        
        self.show_progress(False)
        self.set_status(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", error_message)
    
    def clear_logs(self):
        """Clear the log displays."""
        
        self.log_text.clear()
        self.detailed_log_text.clear()
    
    def save_logs(self):
        """Save logs to file."""
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Logs",
            "power_platform_utility_logs.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.detailed_log_text.toPlainText())
                QMessageBox.information(self, "Success", "Logs saved successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save logs: {str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        
        QMessageBox.about(
            self,
            "About Power Platform Utility",
            "Power Platform Utility v1.0.0\n\n"
            "A PySide6-based GUI application for interfacing with\n"
            "Power Platform environments using the PAC CLI.\n\n"
            "Built with Python and PySide6"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        
        # Save window geometry if configured
        if self.config.get("ui", {}).get("remember_size", True):
            size = self.size()
            self.config["ui"]["window_width"] = size.width()
            self.config["ui"]["window_height"] = size.height()
        
        event.accept()
