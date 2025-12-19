"""
SQLite Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in SQLite.

Usage:
    robot --listener sysbot.plugins.robot.listener.bdd_sqlite.BddSqlite:results.db:MyCampaign tests/

Example:
    robot --listener sysbot.plugins.robot.listener.bdd_sqlite.BddSqlite:results.db:TestRun1 tests/
"""

from .bdd_sql import BddSqlListener


class BddSqlite(BddSqlListener):
    """
    Robot Framework listener that stores test results in SQLite database.
    
    SQLite is a lightweight, file-based database that requires no separate server.
    Perfect for local testing and small to medium-sized test suites.
    """
    
    def _build_connection_url(self) -> str:
        """
        Build SQLAlchemy connection URL for SQLite.
        
        Returns:
            Connection URL string in format: sqlite:///path/to/database.db
        """
        return f"sqlite:///{self.connection_string}"
