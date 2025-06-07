"""
PAC CLI Wrapper Module

This module provides a Python wrapper for the Power Platform CLI (PAC CLI)
to enable easy integration with the GUI application.
"""

import subprocess
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path


class PACCLIError(Exception):
    """Custom exception for PAC CLI related errors."""
    pass


class PACCLIWrapper:
    """
    A Python wrapper for the Power Platform CLI (PAC CLI).
    
    This class provides methods to interact with Power Platform environments,
    solutions, and other resources through the PAC CLI.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._check_pac_installation()
    
    def _check_pac_installation(self) -> bool:
        """Check if PAC CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["pac", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"PAC CLI found: {result.stdout.strip()}")
                return True
            else:
                raise PACCLIError("PAC CLI not found or not accessible")
        except subprocess.TimeoutExpired:
            raise PACCLIError("PAC CLI command timed out")
        except FileNotFoundError:
            raise PACCLIError("PAC CLI not installed. Please install Power Platform CLI first.")
    
    def run_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a PAC CLI command and return the result.
        
        Args:
            command: List of command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Dictionary containing command result and metadata
        """
        full_command = ["pac"] + command
        self.logger.debug(f"Executing command: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": ' '.join(full_command)
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {' '.join(full_command)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1,
                "command": ' '.join(full_command)
            }
    
    def get_environments(self) -> List[Dict[str, Any]]:
        """Get list of Power Platform environments."""
        result = self.run_command(["org", "list", "--json"])
        
        if result["success"]:
            try:
                # Parse JSON output
                environments = json.loads(result["stdout"])
                return environments
            except json.JSONDecodeError:
                self.logger.error("Failed to parse environments JSON response")
                return []
        else:
            self.logger.error(f"Failed to get environments: {result['stderr']}")
            return []
    
    def select_environment(self, environment_url: str) -> bool:
        """Select a Power Platform environment."""
        result = self.run_command(["org", "select", "--environment", environment_url])
        
        if result["success"]:
            self.logger.info(f"Successfully selected environment: {environment_url}")
            return True
        else:
            self.logger.error(f"Failed to select environment: {result['stderr']}")
            return False
    
    def get_solutions(self) -> List[Dict[str, Any]]:
        """Get list of solutions in the current environment."""
        result = self.run_command(["solution", "list", "--json"])
        
        if result["success"]:
            try:
                solutions = json.loads(result["stdout"])
                return solutions
            except json.JSONDecodeError:
                self.logger.error("Failed to parse solutions JSON response")
                return []
        else:
            self.logger.error(f"Failed to get solutions: {result['stderr']}")
            return []
    
    def export_solution(self, solution_name: str, output_path: str, managed: bool = False) -> bool:
        """Export a solution from the current environment."""
        command = [
            "solution", "export",
            "--name", solution_name,
            "--path", output_path
        ]
        
        if managed:
            command.append("--managed")
        
        result = self.run_command(command, timeout=300)  # 5 minutes timeout for export
        
        if result["success"]:
            self.logger.info(f"Successfully exported solution: {solution_name}")
            return True
        else:
            self.logger.error(f"Failed to export solution: {result['stderr']}")
            return False
    
    def import_solution(self, solution_path: str, publish_workflows: bool = True) -> bool:
        """Import a solution to the current environment."""
        command = [
            "solution", "import",
            "--path", solution_path
        ]
        
        if publish_workflows:
            command.append("--publish-changes")
        
        result = self.run_command(command, timeout=600)  # 10 minutes timeout for import
        
        if result["success"]:
            self.logger.info(f"Successfully imported solution: {solution_path}")
            return True
        else:
            self.logger.error(f"Failed to import solution: {result['stderr']}")
            return False
    
    def get_current_environment(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently selected environment."""
        result = self.run_command(["org", "who", "--json"])
        
        if result["success"]:
            try:
                environment_info = json.loads(result["stdout"])
                return environment_info
            except json.JSONDecodeError:
                self.logger.error("Failed to parse current environment JSON response")
                return None
        else:
            self.logger.error(f"Failed to get current environment: {result['stderr']}")
            return None
    
    def authenticate(self) -> bool:
        """Authenticate with Power Platform."""
        result = self.run_command(["auth", "create"])
        
        if result["success"]:
            self.logger.info("Successfully authenticated with Power Platform")
            return True
        else:
            self.logger.error(f"Failed to authenticate: {result['stderr']}")
            return False
