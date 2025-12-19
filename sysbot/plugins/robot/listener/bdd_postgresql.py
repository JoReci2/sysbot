"""
PostgreSQL Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in PostgreSQL.

Usage:
    robot --listener sysbot.plugins.robot.listener.bdd_postgresql.BddPostgresql:postgresql://user:pass@localhost/testdb:MyCampaign tests/

Example:
    robot --listener sysbot.plugins.robot.listener.bdd_postgresql.BddPostgresql:postgresql://postgres:password@localhost/test_results:Sprint42 tests/

Requirements:
    - psycopg2-binary package must be installed
    - PostgreSQL server must be running and accessible
"""

from .bdd_sql import BddSqlListener


class BddPostgresql(BddSqlListener):
    """
    Robot Framework listener that stores test results in PostgreSQL database.
    
    PostgreSQL is a powerful, enterprise-grade relational database suitable for
    large test suites and production environments.
    
    Requires: psycopg2-binary
    Install with: pip install psycopg2-binary
    """
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize PostgreSQL listener.
        
        Args:
            connection_string: PostgreSQL connection string (e.g., postgresql://user:pass@host/db)
            campaign_name: Name of the test campaign
        
        Raises:
            ImportError: If psycopg2 is not installed
        """
        # Check for psycopg2
        try:
            import psycopg2
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install it with: pip install psycopg2-binary")
        
        super().__init__(connection_string, campaign_name)
    
    def _build_connection_url(self) -> str:
        """
        Build SQLAlchemy connection URL for PostgreSQL.
        
        Converts postgresql:// to postgresql+psycopg2:// for SQLAlchemy.
        
        Returns:
            Connection URL string in format: postgresql+psycopg2://user:pass@host/db
        """
        if self.connection_string.startswith("postgresql://"):
            return self.connection_string.replace("postgresql://", "postgresql+psycopg2://", 1)
        return self.connection_string
