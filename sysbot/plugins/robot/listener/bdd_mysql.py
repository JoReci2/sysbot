"""
MySQL Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in MySQL.

Usage:
    robot --listener sysbot.plugins.robot.listener.bdd_mysql.BddMysql:mysql://user:pass@localhost/testdb:MyCampaign tests/

Example:
    robot --listener sysbot.plugins.robot.listener.bdd_mysql.BddMysql:mysql://root:password@localhost/test_results:Sprint42 tests/

Requirements:
    - mysql-connector-python package must be installed
    - MySQL server must be running and accessible
"""

from .bdd_sql import BddSqlListener


class BddMysql(BddSqlListener):
    """
    Robot Framework listener that stores test results in MySQL database.
    
    MySQL is a popular relational database suitable for medium to large test suites
    and team environments where centralized test result storage is needed.
    
    Requires: mysql-connector-python
    Install with: pip install mysql-connector-python
    """
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize MySQL listener.
        
        Args:
            connection_string: MySQL connection string (e.g., mysql://user:pass@host/db)
            campaign_name: Name of the test campaign
        
        Raises:
            ImportError: If mysql-connector-python is not installed
        """
        # Check for mysql-connector-python
        try:
            import mysql.connector
        except ImportError:
            raise ImportError("mysql-connector-python is required for MySQL support. Install it with: pip install mysql-connector-python")
        
        super().__init__(connection_string, campaign_name)
    
    def _build_connection_url(self) -> str:
        """
        Build SQLAlchemy connection URL for MySQL.
        
        Converts mysql:// to mysql+mysqlconnector:// for SQLAlchemy.
        
        Returns:
            Connection URL string in format: mysql+mysqlconnector://user:pass@host/db
        """
        if self.connection_string.startswith("mysql://"):
            return self.connection_string.replace("mysql://", "mysql+mysqlconnector://", 1)
        return self.connection_string
