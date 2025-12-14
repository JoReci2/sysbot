"""
Database Listener Plugin for Robot Framework

This plugin provides a Robot Framework listener that can send test results
to various databases (MongoDB, MySQL, SQLite, PostgreSQL).

Usage:
    robot --listener sysbot.plugins.listener.DatabaseListener:db_type:connection_string tests/

Examples:
    # SQLite
    robot --listener sysbot.plugins.listener.DatabaseListener:sqlite:results.db tests/

    # MySQL
    robot --listener sysbot.plugins.listener.DatabaseListener:mysql:mysql://user:pass@localhost/testdb tests/

    # PostgreSQL
    robot --listener sysbot.plugins.listener.DatabaseListener:postgresql:postgresql://user:pass@localhost/testdb tests/

    # MongoDB
    robot --listener sysbot.plugins.listener.DatabaseListener:mongodb:mongodb://localhost:27017/testdb tests/
"""

import datetime
import json
from typing import Any, Dict, Optional


class DatabaseListener:
    """
    Robot Framework listener that stores test results in a database.
    
    Supports: MongoDB, MySQL, SQLite, PostgreSQL
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, db_type: str = "sqlite", connection_string: str = "test_results.db"):
        """
        Initialize the database listener.
        
        Args:
            db_type: Database type (sqlite, mysql, postgresql, mongodb)
            connection_string: Database connection string or path
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.connection = None
        self.current_suite = None
        self.current_test = None
        
        # Initialize database connection
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """Establish database connection based on type."""
        try:
            if self.db_type == "sqlite":
                self._connect_sqlite()
            elif self.db_type == "mysql":
                self._connect_mysql()
            elif self.db_type == "postgresql":
                self._connect_postgresql()
            elif self.db_type == "mongodb":
                self._connect_mongodb()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            raise Exception(f"Failed to connect to {self.db_type} database: {e}") from e
    
    def _connect_sqlite(self):
        """Connect to SQLite database."""
        import sqlite3
        self.connection = sqlite3.connect(self.connection_string)
        self.connection.row_factory = sqlite3.Row
    
    def _connect_mysql(self):
        """Connect to MySQL database."""
        try:
            import mysql.connector
            from urllib.parse import urlparse
            
            parsed = urlparse(self.connection_string)
            self.connection = mysql.connector.connect(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 3306,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path.lstrip('/') if parsed.path else 'testdb'
            )
        except ImportError:
            raise ImportError("mysql-connector-python is required for MySQL support. Install it with: pip install mysql-connector-python")
    
    def _connect_postgresql(self):
        """Connect to PostgreSQL database."""
        try:
            import psycopg2
            self.connection = psycopg2.connect(self.connection_string)
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install it with: pip install psycopg2-binary")
    
    def _connect_mongodb(self):
        """Connect to MongoDB database."""
        try:
            from pymongo import MongoClient
            from urllib.parse import urlparse
            
            client = MongoClient(self.connection_string)
            parsed = urlparse(self.connection_string)
            db_name = parsed.path.lstrip('/') if parsed.path else 'testdb'
            self.connection = client[db_name]
        except ImportError:
            raise ImportError("pymongo is required for MongoDB support. Install it with: pip install pymongo")
    
    def _initialize_schema(self):
        """Create database tables/collections if they don't exist."""
        if self.db_type == "mongodb":
            # MongoDB doesn't require schema initialization
            pass
        else:
            self._create_sql_tables()
    
    def _create_sql_tables(self):
        """Create SQL tables for storing test results."""
        cursor = self.connection.cursor()
        
        # Determine the auto-increment syntax for the database
        if self.db_type == "sqlite":
            id_column = "id INTEGER PRIMARY KEY AUTOINCREMENT"
        elif self.db_type == "mysql":
            id_column = "id INTEGER PRIMARY KEY AUTO_INCREMENT"
        else:  # postgresql
            id_column = "id SERIAL PRIMARY KEY"
        
        # Suites table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS test_suites (
                {id_column},
                name TEXT NOT NULL,
                doc TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                message TEXT,
                metadata TEXT
            )
        """)
        
        # Tests table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS test_cases (
                {id_column},
                suite_id INTEGER,
                name TEXT NOT NULL,
                doc TEXT,
                tags TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                message TEXT,
                FOREIGN KEY (suite_id) REFERENCES test_suites(id)
            )
        """)
        
        # Keywords table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS keywords (
                {id_column},
                test_id INTEGER,
                name TEXT NOT NULL,
                library TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT,
                message TEXT,
                FOREIGN KEY (test_id) REFERENCES test_cases(id)
            )
        """)
        
        self.connection.commit()
    
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        suite_info = {
            'name': data.name,
            'doc': data.doc or '',
            'start_time': datetime.datetime.now(),
            'metadata': json.dumps(dict(data.metadata)) if hasattr(data, 'metadata') else '{}'
        }
        
        if self.db_type == "mongodb":
            result_doc = self.connection.test_suites.insert_one(suite_info)
            suite_info['_id'] = result_doc.inserted_id
        else:
            cursor = self.connection.cursor()
            if self.db_type == "sqlite" or self.db_type == "mysql":
                cursor.execute("""
                    INSERT INTO test_suites (name, doc, start_time, metadata)
                    VALUES (%s, %s, %s, %s)
                """ if self.db_type == "mysql" else """
                    INSERT INTO test_suites (name, doc, start_time, metadata)
                    VALUES (?, ?, ?, ?)
                """, (suite_info['name'], suite_info['doc'], suite_info['start_time'], suite_info['metadata']))
                suite_info['id'] = cursor.lastrowid
            else:  # PostgreSQL
                cursor.execute("""
                    INSERT INTO test_suites (name, doc, start_time, metadata)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (suite_info['name'], suite_info['doc'], suite_info['start_time'], suite_info['metadata']))
                suite_info['id'] = cursor.fetchone()[0]
            
            self.connection.commit()
        
        self.current_suite = suite_info
    
    def end_suite(self, data, result):
        """Called when a test suite ends."""
        if not self.current_suite:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        if self.db_type == "mongodb":
            self.connection.test_suites.update_one(
                {'_id': self.current_suite['_id']},
                {'$set': {
                    'end_time': end_time,
                    'status': status,
                    'message': message
                }}
            )
        else:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE test_suites
                SET end_time = ?, status = ?, message = ?
                WHERE id = ?
            """ if self.db_type == "sqlite" else """
                UPDATE test_suites
                SET end_time = %s, status = %s, message = %s
                WHERE id = %s
            """, (end_time, status, message, self.current_suite['id']))
            self.connection.commit()
        
        self.current_suite = None
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        if not self.current_suite:
            return
        
        test_info = {
            'suite_id': self.current_suite['id'] if self.db_type != "mongodb" else self.current_suite['_id'],
            'name': data.name,
            'doc': data.doc or '',
            'tags': ','.join(data.tags) if hasattr(data, 'tags') else '',
            'start_time': datetime.datetime.now()
        }
        
        if self.db_type == "mongodb":
            result_doc = self.connection.test_cases.insert_one(test_info)
            test_info['_id'] = result_doc.inserted_id
        else:
            cursor = self.connection.cursor()
            if self.db_type == "sqlite" or self.db_type == "mysql":
                cursor.execute("""
                    INSERT INTO test_cases (suite_id, name, doc, tags, start_time)
                    VALUES (%s, %s, %s, %s, %s)
                """ if self.db_type == "mysql" else """
                    INSERT INTO test_cases (suite_id, name, doc, tags, start_time)
                    VALUES (?, ?, ?, ?, ?)
                """, (test_info['suite_id'], test_info['name'], test_info['doc'], test_info['tags'], test_info['start_time']))
                test_info['id'] = cursor.lastrowid
            else:  # PostgreSQL
                cursor.execute("""
                    INSERT INTO test_cases (suite_id, name, doc, tags, start_time)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (test_info['suite_id'], test_info['name'], test_info['doc'], test_info['tags'], test_info['start_time']))
                test_info['id'] = cursor.fetchone()[0]
            
            self.connection.commit()
        
        self.current_test = test_info
    
    def end_test(self, data, result):
        """Called when a test case ends."""
        if not self.current_test:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        if self.db_type == "mongodb":
            self.connection.test_cases.update_one(
                {'_id': self.current_test['_id']},
                {'$set': {
                    'end_time': end_time,
                    'status': status,
                    'message': message
                }}
            )
        else:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE test_cases
                SET end_time = ?, status = ?, message = ?
                WHERE id = ?
            """ if self.db_type == "sqlite" else """
                UPDATE test_cases
                SET end_time = %s, status = %s, message = %s
                WHERE id = %s
            """, (end_time, status, message, self.current_test['id']))
            self.connection.commit()
        
        self.current_test = None
    
    def start_keyword(self, data, result):
        """Called when a keyword starts."""
        if not self.current_test:
            return
        
        keyword_info = {
            'test_id': self.current_test['id'] if self.db_type != "mongodb" else self.current_test['_id'],
            'name': data.kwname if hasattr(data, 'kwname') else data.name,
            'library': data.libname if hasattr(data, 'libname') else '',
            'start_time': datetime.datetime.now()
        }
        
        if self.db_type == "mongodb":
            self.connection.keywords.insert_one(keyword_info)
        else:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO keywords (test_id, name, library, start_time)
                VALUES (?, ?, ?, ?)
            """ if self.db_type == "sqlite" else """
                INSERT INTO keywords (test_id, name, library, start_time)
                VALUES (%s, %s, %s, %s)
            """, (keyword_info['test_id'], keyword_info['name'], keyword_info['library'], keyword_info['start_time']))
            self.connection.commit()
    
    def end_keyword(self, data, result):
        """Called when a keyword ends."""
        # For simplicity, we don't track keyword end times in this implementation
        # This could be extended to update keyword records if needed
        pass
    
    def close(self):
        """Close database connection."""
        if self.connection:
            if self.db_type == "mongodb":
                self.connection.client.close()
            else:
                self.connection.close()
    
    def __del__(self):
        """Cleanup when listener is destroyed."""
        try:
            self.close()
        except Exception:
            pass
