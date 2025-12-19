"""
SQLite Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in SQLite.

Usage:
    robot --listener sysbot.plugins.robot.listener.sqlite.Sqlite:results.db:MyCampaign tests/

Example:
    robot --listener sysbot.plugins.robot.listener.sqlite.Sqlite:results.db:TestRun1 tests/
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


class Sqlite:
    """
    Robot Framework listener that stores test results in SQLite database.
    
    SQLite is a lightweight, file-based database that requires no separate server.
    Perfect for local testing and small to medium-sized test suites.
    
    The listener creates a hierarchical structure:
    - Test Campaign (top level)
      - Test Suite
        - Test Case
          - Keyword
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize the SQLite listener.
        
        Args:
            connection_string: Path to SQLite database file
            campaign_name: Name of the test campaign (default: "Default Campaign")
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for SQL database support. Install it with: pip install sqlalchemy")
        
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
        """Safely extract and convert metadata to JSON string."""
        try:
            if hasattr(data, 'metadata') and data.metadata:
                return json.dumps(dict(data.metadata))
        except (TypeError, ValueError):
            pass
        return '{}'
    
    def _connect(self):
        """Establish database connection using SQLAlchemy."""
        try:
            url = f"sqlite:///{self.connection_string}"
            self.engine = create_engine(url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except Exception as e:
            raise Exception(f"Failed to connect to SQLite database: {e}") from e
    
    def _initialize_schema(self):
        """Create SQL database tables using SQLAlchemy."""
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
        """Create a new campaign or get existing one."""
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
        """Called when a test suite ends."""
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
        """Called when a test case starts."""
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
        """Called when a test case ends."""
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
        """Called when a keyword starts."""
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
        """Called when a keyword ends."""
        # For simplicity, we don't track keyword end times in this implementation
        pass
    
    def close(self):
        """Close database connection and update campaign end time."""
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
        """Cleanup when listener is destroyed."""
        try:
            self.close()
        except Exception:
            pass
