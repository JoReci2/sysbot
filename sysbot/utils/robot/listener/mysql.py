"""
MySQL Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in MySQL.

Usage:
    robot --listener sysbot.utils.robot.listener.mysql.Mysql:mysql://user:pass@localhost/testdb:MyCampaign tests/

Example:
    robot --listener sysbot.utils.robot.listener.mysql.Mysql:mysql://root:password@localhost/test_results:Sprint42 tests/

Requirements:
    - mysql-connector-python package must be installed
    - MySQL server must be running and accessible
"""

import datetime
import json

# SQLAlchemy imports
try:
    from sqlalchemy import Table, Column, Integer, String, DateTime, Text, ForeignKey, MetaData, create_engine, select
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class Mysql:
    """
    Robot Framework listener that stores test results in MySQL database.
    
    MySQL is a popular relational database suitable for medium to large test suites
    and team environments where centralized test result storage is needed.
    
    The listener creates a hierarchical structure:
    - Test Campaign (top level)
      - Test Suite
        - Test Case
          - Keyword
    
    Requires: mysql-connector-python
    Install with: pip install mysql-connector-python
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize the MySQL listener.
        
        Args:
            connection_string: MySQL connection string (e.g., mysql://user:pass@host/db)
            campaign_name: Name of the test campaign (default: "Default Campaign")
        
        Raises:
            ImportError: If SQLAlchemy or mysql-connector-python is not installed
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for SQL database support. Install it with: pip install sqlalchemy")
        
        # Check for mysql-connector-python
        try:
            import mysql.connector
        except ImportError:
            raise ImportError("mysql-connector-python is required for MySQL support. Install it with: pip install mysql-connector-python")
        
        self.connection_string = connection_string
        self.campaign_name = campaign_name
        self.session = None
        self.engine = None
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
    
    def _get_metadata(self, data):
        """
        Safely extract and convert metadata to JSON string.
        
        Args:
            data: Robot Framework data object containing metadata.
        
        Returns:
            JSON string representation of metadata, or empty JSON object if unavailable.
        """
        try:
            if hasattr(data, 'metadata') and data.metadata:
                return json.dumps(dict(data.metadata))
        except (TypeError, ValueError):
            pass
        return '{}'
    
    def _connect(self):
        """
        Establish database connection using SQLAlchemy.
        
        Raises:
            Exception: If connection to MySQL database fails.
        """
        try:
            # Convert mysql:// to mysql+mysqlconnector:// for SQLAlchemy
            if self.connection_string.startswith("mysql://"):
                url = self.connection_string.replace("mysql://", "mysql+mysqlconnector://", 1)
            else:
                url = self.connection_string
            
            self.engine = create_engine(url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except Exception as e:
            raise Exception(f"Failed to connect to MySQL database: {e}") from e
    
    def _initialize_schema(self):
        """
        Create SQL database tables using SQLAlchemy.
        
        Creates tables for test campaigns, test suites, test cases, and keywords
        with appropriate foreign key relationships.
        """
        # Create metadata instance
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
        """
        Create a new campaign or get existing one.
        
        Creates a new test campaign record in the database if it doesn't exist,
        or retrieves the existing campaign with the same name.
        """
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
        """
        Called when a test suite starts.
        
        Args:
            data: Robot Framework suite data object.
            result: Robot Framework suite result object.
        """
        suite_info = {
            'campaign_id': self.current_campaign['id'],
            'name': data.name,
            'doc': data.doc or '',
            'start_time': datetime.datetime.now(),
            'metadata': self._get_metadata(data)
        }
        
        ins = self.test_suites_table.insert().values(**suite_info)
        result = self.session.execute(ins)
        self.session.flush()
        suite_info['id'] = result.inserted_primary_key[0]
        
        self.current_suite = suite_info
    
    def end_suite(self, data, result):
        """
        Called when a test suite ends.
        
        Args:
            data: Robot Framework suite data object.
            result: Robot Framework suite result object.
        """
        if not self.current_suite:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        upd = self.test_suites_table.update().where(
            self.test_suites_table.c.id == self.current_suite['id']
        ).values(
            end_time=end_time,
            status=status,
            message=message
        )
        self.session.execute(upd)
        self.session.commit()
        
        self.current_suite = None
    
    def start_test(self, data, result):
        """
        Called when a test case starts.
        
        Args:
            data: Robot Framework test data object.
            result: Robot Framework test result object.
        """
        if not self.current_suite:
            return
        
        test_info = {
            'suite_id': self.current_suite['id'],
            'name': data.name,
            'doc': data.doc or '',
            'tags': ','.join(data.tags) if hasattr(data, 'tags') and data.tags else '',
            'start_time': datetime.datetime.now()
        }
        
        ins = self.test_cases_table.insert().values(**test_info)
        result = self.session.execute(ins)
        self.session.flush()
        test_info['id'] = result.inserted_primary_key[0]
        
        self.current_test = test_info
    
    def end_test(self, data, result):
        """
        Called when a test case ends.
        
        Args:
            data: Robot Framework test data object.
            result: Robot Framework test result object.
        """
        if not self.current_test:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        upd = self.test_cases_table.update().where(
            self.test_cases_table.c.id == self.current_test['id']
        ).values(
            end_time=end_time,
            status=status,
            message=message
        )
        self.session.execute(upd)
        self.session.flush()
        
        self.current_test = None
    
    def start_keyword(self, data, result):
        """
        Called when a keyword starts.
        
        Args:
            data: Robot Framework keyword data object.
            result: Robot Framework keyword result object.
        """
        if not self.current_test:
            return
        
        keyword_info = {
            'test_id': self.current_test['id'],
            'name': getattr(data, 'kwname', None) or getattr(data, 'name', 'Unknown'),
            'library': getattr(data, 'libname', ''),
            'start_time': datetime.datetime.now()
        }
        
        ins = self.keywords_table.insert().values(**keyword_info)
        self.session.execute(ins)
        self.session.flush()
    
    def end_keyword(self, data, result):
        """
        Called when a keyword ends.
        
        Args:
            data: Robot Framework keyword data object.
            result: Robot Framework keyword result object.
        """
        # For simplicity, we don't track keyword end times in this implementation
        pass
    
    def close(self):
        """
        Close database connection and update campaign end time.
        
        Updates the campaign end timestamp, commits pending transactions,
        and closes the database connection.
        """
        # Update campaign end time
        if self.current_campaign:
            end_time = datetime.datetime.now()
            try:
                upd = self.test_campaigns_table.update().where(
                    self.test_campaigns_table.c.id == self.current_campaign['id']
                ).values(end_time=end_time)
                self.session.execute(upd)
                self.session.commit()
            except Exception:
                pass
        
        # Close connections
        if self.session:
            try:
                self.session.commit()
                self.session.close()
            except Exception:
                pass
        if self.engine:
            try:
                self.engine.dispose()
            except Exception:
                pass
    
    def __del__(self):
        """
        Cleanup when listener is destroyed.
        
        Ensures database connection is properly closed when the listener
        object is garbage collected.
        """
        try:
            self.close()
        except Exception:
            pass
