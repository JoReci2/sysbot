"""
Base Listener for Robot Framework BDD Database Integration

This module provides the base class for Robot Framework listeners that store
test results in databases. It defines the common interface and shared functionality
for all database-specific implementations.
"""

import datetime
import json
from typing import Any, Dict, Optional


class BddBaseListener:
    """
    Base class for Robot Framework database listeners.
    
    This abstract base class defines the common interface for storing test results
    in databases. Specific database implementations should inherit from this class
    and implement the database-specific methods.
    
    The listener creates a hierarchical structure:
    - Test Campaign (top level)
      - Test Suite
        - Test Case
          - Keyword
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize the base listener.
        
        Args:
            connection_string: Database connection string or path
            campaign_name: Name of the test campaign (default: "Default Campaign")
        """
        self.connection_string = connection_string
        self.campaign_name = campaign_name
        self.current_campaign = None
        self.current_suite = None
        self.current_test = None
    
    def _get_metadata(self, data):
        """Safely extract and convert metadata to JSON string."""
        try:
            if hasattr(data, 'metadata') and data.metadata:
                return json.dumps(dict(data.metadata))
        except (TypeError, ValueError):
            pass
        return '{}'
    
    # Abstract methods to be implemented by subclasses
    def _connect(self):
        """Establish database connection. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _connect()")
    
    def _initialize_schema(self):
        """Create database tables/collections. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _initialize_schema()")
    
    def _create_or_get_campaign(self):
        """Create or retrieve test campaign. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _create_or_get_campaign()")
    
    # Robot Framework listener methods
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        raise NotImplementedError("Subclasses must implement start_suite()")
    
    def end_suite(self, data, result):
        """Called when a test suite ends."""
        raise NotImplementedError("Subclasses must implement end_suite()")
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        raise NotImplementedError("Subclasses must implement start_test()")
    
    def end_test(self, data, result):
        """Called when a test case ends."""
        raise NotImplementedError("Subclasses must implement end_test()")
    
    def start_keyword(self, data, result):
        """Called when a keyword starts."""
        raise NotImplementedError("Subclasses must implement start_keyword()")
    
    def end_keyword(self, data, result):
        """Called when a keyword ends."""
        # Default implementation: most implementations don't track keyword end times
        pass
    
    def close(self):
        """Close database connection. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement close()")
    
    def __del__(self):
        """Cleanup when listener is destroyed."""
        try:
            self.close()
        except Exception:
            pass
