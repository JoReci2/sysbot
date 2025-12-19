"""
MongoDB Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in MongoDB.

Usage:
    robot --listener sysbot.plugins.robot.listener.bdd_mongodb.BddMongodb:mongodb://localhost:27017/testdb:MyCampaign tests/

Example:
    robot --listener sysbot.plugins.robot.listener.bdd_mongodb.BddMongodb:mongodb://localhost:27017/test_results:Sprint42 tests/

Requirements:
    - pymongo package must be installed
    - MongoDB server must be running and accessible
"""

import datetime
from urllib.parse import urlparse

from .bdd_base import BddBaseListener


class BddMongodb(BddBaseListener):
    """
    Robot Framework listener that stores test results in MongoDB database.
    
    MongoDB is a NoSQL document database suitable for flexible schema requirements
    and high-volume test result storage.
    
    Requires: pymongo
    Install with: pip install pymongo
    """
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize MongoDB listener.
        
        Args:
            connection_string: MongoDB connection string (e.g., mongodb://host:port/database)
            campaign_name: Name of the test campaign
        
        Raises:
            ImportError: If pymongo is not installed
        """
        self.connection = None
        
        super().__init__(connection_string, campaign_name)
        
        # Initialize database connection
        self._connect()
        self._initialize_schema()
        self._create_or_get_campaign()
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(self.connection_string)
            parsed = urlparse(self.connection_string)
            db_name = parsed.path.lstrip('/') if parsed.path else 'testdb'
            self.connection = client[db_name]
        except ImportError:
            raise ImportError("pymongo is required for MongoDB support. Install it with: pip install pymongo")
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {e}") from e
    
    def _initialize_schema(self):
        """
        Initialize MongoDB schema.
        
        MongoDB doesn't require explicit schema initialization as it's schema-less,
        but we keep this method for interface consistency.
        """
        pass
    
    def _create_or_get_campaign(self):
        """Create a new campaign or get existing one."""
        # Check if campaign exists
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
    
    def start_suite(self, data, result):
        """Called when a test suite starts."""
        suite_info = {
            'campaign_id': self.current_campaign['_id'],
            'name': data.name,
            'doc': data.doc or '',
            'start_time': datetime.datetime.now(),
            'metadata': self._get_metadata(data)
        }
        
        result_doc = self.connection.test_suites.insert_one(suite_info)
        suite_info['_id'] = result_doc.inserted_id
        
        self.current_suite = suite_info
    
    def end_suite(self, data, result):
        """Called when a test suite ends."""
        if not self.current_suite:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        self.connection.test_suites.update_one(
            {'_id': self.current_suite['_id']},
            {'$set': {
                'end_time': end_time,
                'status': status,
                'message': message
            }}
        )
        
        self.current_suite = None
    
    def start_test(self, data, result):
        """Called when a test case starts."""
        if not self.current_suite:
            return
        
        test_info = {
            'suite_id': self.current_suite['_id'],
            'name': data.name,
            'doc': data.doc or '',
            'tags': ','.join(data.tags) if hasattr(data, 'tags') and data.tags else '',
            'start_time': datetime.datetime.now()
        }
        
        result_doc = self.connection.test_cases.insert_one(test_info)
        test_info['_id'] = result_doc.inserted_id
        
        self.current_test = test_info
    
    def end_test(self, data, result):
        """Called when a test case ends."""
        if not self.current_test:
            return
        
        end_time = datetime.datetime.now()
        status = result.status
        message = result.message or ''
        
        self.connection.test_cases.update_one(
            {'_id': self.current_test['_id']},
            {'$set': {
                'end_time': end_time,
                'status': status,
                'message': message
            }}
        )
        
        self.current_test = None
    
    def start_keyword(self, data, result):
        """Called when a keyword starts."""
        if not self.current_test:
            return
        
        keyword_info = {
            'test_id': self.current_test['_id'],
            'name': getattr(data, 'kwname', None) or getattr(data, 'name', 'Unknown'),
            'library': getattr(data, 'libname', ''),
            'start_time': datetime.datetime.now()
        }
        
        self.connection.keywords.insert_one(keyword_info)
    
    def close(self):
        """Close database connection and update campaign end time."""
        # Update campaign end time
        if self.current_campaign:
            end_time = datetime.datetime.now()
            try:
                self.connection.test_campaigns.update_one(
                    {'_id': self.current_campaign['_id']},
                    {'$set': {'end_time': end_time}}
                )
            except Exception:
                pass
        
        # Close connection
        if self.connection:
            try:
                self.connection.client.close()
            except (AttributeError, Exception):
                pass
