"""
Environment Management Module

This module handles Power Platform environment operations and data management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PowerPlatformEnvironment:
    """Data class representing a Power Platform environment."""
    
    name: str
    display_name: str
    url: str
    region: str
    environment_type: str
    state: str
    created_time: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.name})"


class EnvironmentManager:
    """
    Manages Power Platform environments and related operations.
    """
    
    def __init__(self, pac_cli_wrapper):
        self.pac_cli = pac_cli_wrapper
        self.logger = logging.getLogger(__name__)
        self._environments: List[PowerPlatformEnvironment] = []
        self._current_environment: Optional[PowerPlatformEnvironment] = None
    
    def refresh_environments(self) -> bool:
        """Refresh the list of available environments."""
        try:
            env_data = self.pac_cli.get_environments()
            self._environments = []
            
            for env in env_data:
                environment = PowerPlatformEnvironment(
                    name=env.get('EnvironmentName', ''),
                    display_name=env.get('FriendlyName', ''),
                    url=env.get('EnvironmentUrl', ''),
                    region=env.get('Region', ''),
                    environment_type=env.get('EnvironmentType', ''),
                    state=env.get('State', ''),
                    created_time=self._parse_datetime(env.get('CreatedTime'))
                )
                self._environments.append(environment)
            
            self.logger.info(f"Refreshed {len(self._environments)} environments")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh environments: {str(e)}")
            return False
    
    def _parse_datetime(self, date_string: str) -> Optional[datetime]:
        """Parse datetime string from Power Platform API."""
        if not date_string:
            return None
        
        try:
            # Try common datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            self.logger.warning(f"Could not parse datetime: {date_string}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing datetime {date_string}: {str(e)}")
            return None
    
    def get_environments(self) -> List[PowerPlatformEnvironment]:
        """Get the list of available environments."""
        return self._environments.copy()
    
    def select_environment(self, environment: PowerPlatformEnvironment) -> bool:
        """Select an environment as the current working environment."""
        try:
            success = self.pac_cli.select_environment(environment.url)
            if success:
                self._current_environment = environment
                self.logger.info(f"Selected environment: {environment.display_name}")
                return True
            else:
                self.logger.error(f"Failed to select environment: {environment.display_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error selecting environment: {str(e)}")
            return False
    
    def get_current_environment(self) -> Optional[PowerPlatformEnvironment]:
        """Get the currently selected environment."""
        return self._current_environment
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get a summary of all environments by type and region."""
        summary = {
            "total": len(self._environments),
            "by_type": {},
            "by_region": {},
            "by_state": {}
        }
        
        for env in self._environments:
            # Count by type
            env_type = env.environment_type or "Unknown"
            summary["by_type"][env_type] = summary["by_type"].get(env_type, 0) + 1
            
            # Count by region
            region = env.region or "Unknown"
            summary["by_region"][region] = summary["by_region"].get(region, 0) + 1
            
            # Count by state
            state = env.state or "Unknown"
            summary["by_state"][state] = summary["by_state"].get(state, 0) + 1
        
        return summary
    
    def search_environments(self, query: str) -> List[PowerPlatformEnvironment]:
        """Search environments by name or display name."""
        query_lower = query.lower()
        return [
            env for env in self._environments
            if query_lower in env.name.lower() or query_lower in env.display_name.lower()
        ]
