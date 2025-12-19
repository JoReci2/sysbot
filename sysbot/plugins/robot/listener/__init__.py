"""
Robot Framework Listener Plugins

This package provides Robot Framework listeners for storing test results
in various databases.

Available listeners:
    - Bdd: Factory class for backward compatibility (delegates to specific implementations)
    - BddSqlite: SQLite database listener
    - BddMysql: MySQL database listener
    - BddPostgresql: PostgreSQL database listener
    - BddMongodb: MongoDB database listener
"""

from .bdd import Bdd
from .bdd_sqlite import BddSqlite
from .bdd_mysql import BddMysql
from .bdd_postgresql import BddPostgresql
from .bdd_mongodb import BddMongodb

__all__ = [
    'Bdd',
    'BddSqlite',
    'BddMysql',
    'BddPostgresql',
    'BddMongodb',
]
