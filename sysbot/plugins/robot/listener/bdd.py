"""
Database Listener Plugin for Robot Framework

This plugin provides a Robot Framework listener that can send test results
to various databases (MongoDB, MySQL, SQLite, PostgreSQL).

This module provides backward compatibility by acting as a factory that delegates
to specific database listener implementations.

Usage:
    robot --listener sysbot.plugins.robot.listener.bdd.Bdd:db_type:connection_string:campaign_name tests/

Examples:
    # SQLite
    robot --listener sysbot.plugins.robot.listener.bdd.Bdd:sqlite:results.db:MyCampaign tests/

    # MySQL
    robot --listener sysbot.plugins.robot.listener.bdd.Bdd:mysql:mysql://user:pass@localhost/testdb:MyCampaign tests/

    # PostgreSQL
    robot --listener sysbot.plugins.robot.listener.bdd.Bdd:postgresql:postgresql://user:pass@localhost/testdb:MyCampaign tests/

    # MongoDB
    robot --listener sysbot.plugins.robot.listener.bdd.Bdd:mongodb:mongodb://localhost:27017/testdb:MyCampaign tests/

Note: For new code, consider using the specific listener classes directly:
    - BddSqlite for SQLite databases
    - BddMysql for MySQL databases
    - BddPostgresql for PostgreSQL databases
    - BddMongodb for MongoDB databases
"""

from .bdd_sqlite import BddSqlite
from .bdd_mysql import BddMysql
from .bdd_postgresql import BddPostgresql
from .bdd_mongodb import BddMongodb


class Bdd:
    """
    Factory class for Robot Framework database listeners.
    
    This class maintains backward compatibility with the original monolithic implementation
    by delegating to specific database listener classes based on the db_type parameter.
    
    Supports: MongoDB, MySQL, SQLite, PostgreSQL
    
    The listener creates a hierarchical structure:
    - Test Campaign (top level)
      - Test Suite
        - Test Case
          - Keyword
    
    Note: Keyword tracking currently captures start time and name but not end time or status.
          This is sufficient for most use cases where test-level tracking is the primary concern.
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, db_type: str = "sqlite", connection_string: str = "test_results.db", campaign_name: str = "Default Campaign"):
        """
        Create and delegate to the appropriate database listener instance.
        
        Args:
            db_type: Database type (sqlite, mysql, postgresql, mongodb)
            connection_string: Database connection string or path
            campaign_name: Name of the test campaign (default: "Default Campaign")
        
        Raises:
            ValueError: If db_type is not supported
        """
        db_type = db_type.lower()
        
        if db_type == "sqlite":
            self._listener = BddSqlite(connection_string, campaign_name)
        elif db_type == "mysql":
            self._listener = BddMysql(connection_string, campaign_name)
        elif db_type == "postgresql":
            self._listener = BddPostgresql(connection_string, campaign_name)
        elif db_type == "mongodb":
            self._listener = BddMongodb(connection_string, campaign_name)
        else:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types: sqlite, mysql, postgresql, mongodb")
    
    # Delegate all listener methods to the underlying listener
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        return self._listener.start_suite(data, result)
    
    def end_suite(self, data, result):
        """Called when a test suite ends."""
        return self._listener.end_suite(data, result)
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        return self._listener.start_test(data, result)
    
    def end_test(self, data, result):
        """Called when a test case ends."""
        return self._listener.end_test(data, result)
    
    def start_keyword(self, data, result):
        """Called when a keyword starts."""
        return self._listener.start_keyword(data, result)
    
    def end_keyword(self, data, result):
        """Called when a keyword ends."""
        return self._listener.end_keyword(data, result)
    
    def close(self):
        """Close database connection."""
        return self._listener.close()
    
    def __del__(self):
        """Cleanup when listener is destroyed."""
        try:
            self.close()
        except Exception:
            pass


