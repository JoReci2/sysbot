"""
Robot Framework Listener Package

This package provides listener implementations for storing Robot Framework
test execution results in various database systems. Each listener creates a
hierarchical structure: Campaign → Suite → Test Case → Keyword.

Available listeners:
- sqlite: SQLite database listener
- mysql: MySQL database listener
- postgresql: PostgreSQL database listener
- mongodb: MongoDB database listener
"""
