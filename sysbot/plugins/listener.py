"""
Database Listener Plugin for Robot Framework

This plugin provides a Robot Framework listener that can send test results
to various databases (MongoDB, MySQL, SQLite, PostgreSQL).

Usage:
    robot --listener sysbot.plugins.listener.DatabaseListener:db_type:connection_string:campaign_name tests/

Examples:
    # SQLite
    robot --listener sysbot.plugins.listener.DatabaseListener:sqlite:results.db:MyCampaign tests/

    # MySQL
    robot --listener sysbot.plugins.listener.DatabaseListener:mysql:mysql://user:pass@localhost/testdb:MyCampaign tests/

    # PostgreSQL
    robot --listener sysbot.plugins.listener.DatabaseListener:postgresql:postgresql://user:pass@localhost/testdb:MyCampaign tests/

    # MongoDB
    robot --listener sysbot.plugins.listener.DatabaseListener:mongodb:mongodb://localhost:27017/testdb:MyCampaign tests/
"""

import datetime
import json
from typing import Any, Dict, Optional

# SQLAlchemy imports (will be used for SQL databases)
try:
    from sqlalchemy import Table, Column, Integer, String, DateTime, Text, ForeignKey, MetaData, create_engine
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class DatabaseListener:
    """
    Robot Framework listener that stores test results in a database.
    
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
        Initialize the database listener.
        
        Args:
            db_type: Database type (sqlite, mysql, postgresql, mongodb)
            connection_string: Database connection string or path
            campaign_name: Name of the test campaign (default: "Default Campaign")
        """
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.campaign_name = campaign_name
        self.session = None
        self.engine = None
        self.connection = None
        self.metadata = None
        self.test_campaigns_table = None
        self.test_suites_table = None
        self.test_cases_table = None
        self.keywords_table = None
        self.current_campaign = None
        self.current_suite = None
        self.current_test = None
        
        # Initialize database connection
        self._connect()
        self._initialize_schema()
        self._create_or_get_campaign()
    
    def _connect(self):
        """Establish database connection based on type."""
        try:
            if self.db_type == "mongodb":
                self._connect_mongodb()
            else:
                self._connect_sql()
        except Exception as e:
            raise Exception(f"Failed to connect to {self.db_type} database: {e}") from e
    
    def _connect_sql(self):
        """Connect to SQL database using SQLAlchemy."""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for SQL database support. Install it with: pip install sqlalchemy")
        
        try:
            # Build connection URL
            if self.db_type == "sqlite":
                url = f"sqlite:///{self.connection_string}"
            elif self.db_type == "mysql":
                # Check for mysql-connector-python
                try:
                    import mysql.connector
                except ImportError:
                    raise ImportError("mysql-connector-python is required for MySQL support. Install it with: pip install mysql-connector-python")
                
                # Ensure mysql:// is replaced with mysql+mysqlconnector://
                if self.connection_string.startswith("mysql://"):
                    url = self.connection_string.replace("mysql://", "mysql+mysqlconnector://", 1)
                else:
                    url = self.connection_string
            elif self.db_type == "postgresql":
                # Check for psycopg2
                try:
                    import psycopg2
                except ImportError:
                    raise ImportError("psycopg2 is required for PostgreSQL support. Install it with: pip install psycopg2-binary")
                
                # Ensure postgresql:// is replaced with postgresql+psycopg2://
                if self.connection_string.startswith("postgresql://"):
                    url = self.connection_string.replace("postgresql://", "postgresql+psycopg2://", 1)
                else:
                    url = self.connection_string
            else:
                raise ValueError(f"Unsupported SQL database type: {self.db_type}")
            
            self.engine = create_engine(url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
        except ImportError:
            raise
        except Exception as e:
            raise Exception(f"Failed to connect to SQL database: {e}") from e
    
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
    
    def _get_metadata(self, data):
        """Safely extract and convert metadata to JSON string."""
        try:
            if hasattr(data, 'metadata') and data.metadata:
                return json.dumps(dict(data.metadata))
        except (TypeError, ValueError):
            pass
        return '{}'
    
    def _initialize_schema(self):
        """Create database tables/collections if they don't exist."""
        if self.db_type == "mongodb":
            # MongoDB doesn't require schema initialization
            pass
        else:
            self._create_sql_tables()
    
    def _create_sql_tables(self):
        """Create SQL tables using SQLAlchemy."""
        # Create metadata instance once
        self.metadata = MetaData()
        
        # Define test_campaigns table (top level)
        self.test_campaigns_table = Table('test_campaigns', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('name', String(500), nullable=False),
            Column('start_time', DateTime),
            Column('end_time', DateTime),
            Column('description', Text)
        )
        
        # Define test_suites table
        self.test_suites_table = Table('test_suites', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('campaign_id', Integer, ForeignKey('test_campaigns.id')),
            Column('name', String(500), nullable=False),
            Column('doc', Text),
            Column('start_time', DateTime),
            Column('end_time', DateTime),
            Column('status', String(50)),
            Column('message', Text),
            Column('metadata', Text)
        )
        
        # Define test_cases table
        self.test_cases_table = Table('test_cases', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('suite_id', Integer, ForeignKey('test_suites.id')),
            Column('name', String(500), nullable=False),
            Column('doc', Text),
            Column('tags', Text),
            Column('start_time', DateTime),
            Column('end_time', DateTime),
            Column('status', String(50)),
            Column('message', Text)
        )
        
        # Define keywords table
        self.keywords_table = Table('keywords', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('test_id', Integer, ForeignKey('test_cases.id')),
            Column('name', String(500), nullable=False),
            Column('library', String(255)),
            Column('start_time', DateTime),
            Column('end_time', DateTime),
            Column('status', String(50)),
            Column('message', Text)
        )
        
        # Create all tables
        self.metadata.create_all(self.engine)
    
    def _create_or_get_campaign(self):
        """Create a new campaign or get existing one."""
        if self.db_type == "mongodb":
            # For MongoDB, check if campaign exists
            existing = self.connection.test_campaigns.find_one({'name': self.campaign_name})
            if existing:
                self.current_campaign = existing
            else:
                campaign_info = {
                    'name': self.campaign_name,
                    'start_time': datetime.datetime.now(),
                    'description': f'Test campaign: {self.campaign_name}'
                }
                result_doc = self.connection.test_campaigns.insert_one(campaign_info)
                campaign_info['_id'] = result_doc.inserted_id
                self.current_campaign = campaign_info
        else:
            # For SQL databases, create or get campaign
            from sqlalchemy import select
            
            # Check if campaign exists
            stmt = select(self.test_campaigns_table).where(
                self.test_campaigns_table.c.name == self.campaign_name
            )
            result = self.session.execute(stmt).fetchone()
            
            if result:
                self.current_campaign = {
                    'id': result[0],
                    'name': result[1],
                    'start_time': result[2],
                    'end_time': result[3],
                    'description': result[4]
                }
            else:
                # Create new campaign
                campaign_info = {
                    'name': self.campaign_name,
                    'start_time': datetime.datetime.now(),
                    'description': f'Test campaign: {self.campaign_name}'
                }
                ins = self.test_campaigns_table.insert().values(**campaign_info)
                result = self.session.execute(ins)
                self.session.commit()
                campaign_info['id'] = result.inserted_primary_key[0]
                self.current_campaign = campaign_info
    
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        suite_info = {
            'campaign_id': self.current_campaign['id'] if self.db_type != "mongodb" else self.current_campaign['_id'],
            'name': data.name,
            'doc': data.doc or '',
            'start_time': datetime.datetime.now(),
            'metadata': self._get_metadata(data)
        }
        
        if self.db_type == "mongodb":
            result_doc = self.connection.test_suites.insert_one(suite_info)
            suite_info['_id'] = result_doc.inserted_id
        else:
            # Insert using SQLAlchemy
            ins = self.test_suites_table.insert().values(**suite_info)
            result = self.session.execute(ins)
            self.session.flush()  # Use flush instead of commit for better performance
            suite_info['id'] = result.inserted_primary_key[0]
        
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
            # Update using SQLAlchemy
            upd = self.test_suites_table.update().where(
                self.test_suites_table.c.id == self.current_suite['id']
            ).values(
                end_time=end_time,
                status=status,
                message=message
            )
            self.session.execute(upd)
            self.session.commit()  # Commit at suite end to persist all suite data
        
        self.current_suite = None
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        if not self.current_suite:
            return
        
        test_info = {
            'suite_id': self.current_suite['id'] if self.db_type != "mongodb" else self.current_suite['_id'],
            'name': data.name,
            'doc': data.doc or '',
            'tags': ','.join(data.tags) if hasattr(data, 'tags') and data.tags else '',
            'start_time': datetime.datetime.now()
        }
        
        if self.db_type == "mongodb":
            result_doc = self.connection.test_cases.insert_one(test_info)
            test_info['_id'] = result_doc.inserted_id
        else:
            # Insert using SQLAlchemy
            ins = self.test_cases_table.insert().values(**test_info)
            result = self.session.execute(ins)
            self.session.flush()  # Use flush instead of commit
            test_info['id'] = result.inserted_primary_key[0]
        
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
            # Update using SQLAlchemy
            upd = self.test_cases_table.update().where(
                self.test_cases_table.c.id == self.current_test['id']
            ).values(
                end_time=end_time,
                status=status,
                message=message
            )
            self.session.execute(upd)
            self.session.flush()  # Use flush instead of commit
        
        self.current_test = None
    
    def start_keyword(self, data, result):
        """Called when a keyword starts."""
        if not self.current_test:
            return
        
        keyword_info = {
            'test_id': self.current_test['id'] if self.db_type != "mongodb" else self.current_test['_id'],
            'name': getattr(data, 'kwname', None) or getattr(data, 'name', 'Unknown'),
            'library': getattr(data, 'libname', ''),
            'start_time': datetime.datetime.now()
        }
        
        if self.db_type == "mongodb":
            self.connection.keywords.insert_one(keyword_info)
        else:
            # Insert using SQLAlchemy
            ins = self.keywords_table.insert().values(**keyword_info)
            self.session.execute(ins)
            self.session.flush()  # Use flush instead of commit
    
    def end_keyword(self, data, result):
        """Called when a keyword ends."""
        # For simplicity, we don't track keyword end times in this implementation
        # This could be extended to update keyword records if needed
        pass
    
    def close(self):
        """Close database connection and update campaign end time."""
        # Update campaign end time
        if self.current_campaign:
            end_time = datetime.datetime.now()
            if self.db_type == "mongodb":
                try:
                    self.connection.test_campaigns.update_one(
                        {'_id': self.current_campaign['_id']},
                        {'$set': {'end_time': end_time}}
                    )
                except Exception:
                    pass
            else:
                try:
                    upd = self.test_campaigns_table.update().where(
                        self.test_campaigns_table.c.id == self.current_campaign['id']
                    ).values(end_time=end_time)
                    self.session.execute(upd)
                    self.session.commit()  # Commit campaign end time update
                except Exception:
                    pass
        
        # Close connections
        if self.db_type == "mongodb":
            if self.connection:
                try:
                    self.connection.client.close()
                except (AttributeError, Exception):
                    # Handle case where client attribute might not exist
                    pass
        else:
            if self.session:
                try:
                    self.session.commit()  # Commit any remaining pending changes
                    self.session.close()
                except Exception:
                    pass
            if self.engine:
                try:
                    self.engine.dispose()
                except Exception:
                    pass
    
    def __del__(self):
        """Cleanup when listener is destroyed."""
        try:
            self.close()
        except Exception:
            pass
