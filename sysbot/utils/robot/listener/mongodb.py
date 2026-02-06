"""
MongoDB Listener for Robot Framework BDD Database Integration

This module provides a Robot Framework listener that stores test results in MongoDB.

Usage:
    robot --listener sysbot.utils.robot.listener.mongodb.Mongodb:mongodb://localhost:27017/testdb:MyCampaign your_tests/

Example:
    robot --listener sysbot.utils.robot.listener.mongodb.Mongodb:mongodb://localhost:27017/test_results:Sprint42 your_tests/

Requirements:
    - pymongo package must be installed
    - MongoDB server must be running and accessible
"""

import datetime
import json
from urllib.parse import urlparse


class Mongodb:
    """
    Robot Framework listener that stores test results in MongoDB database.
    
    MongoDB is a NoSQL document database suitable for flexible schema requirements
    and high-volume test result storage.
    
    The listener creates a hierarchical structure:
    - Test Campaign (top level)
      - Test Suite
        - Test Case
          - Keyword
    
    Requires: pymongo
    Install with: pip install pymongo
    """
    
    ROBOT_LISTENER_API_VERSION = 3
    
    def __init__(self, connection_string: str, campaign_name: str = "Default Campaign"):
        """
        Initialize MongoDB listener.
        
        Args:
            connection_string: MongoDB connection string (e.g., mongodb://host:port/database)
            campaign_name: Name of the test campaign
        
        Raises:
            ImportError: If pymongo is not installed
        """
        self.connection_string = connection_string
        self.campaign_name = campaign_name
        self.connection = None
        self.current_campaign = None
        self.current_suite = None
        self.current_test = None
        
        # Initialize database connection
        self._connect()
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
        Establish MongoDB connection.
        
        Raises:
            ImportError: If pymongo package is not installed.
            Exception: If connection to MongoDB fails.
        """
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
    
    def _create_or_get_campaign(self):
        """
        Create a new campaign or get existing one.
        
        Creates a new test campaign document in MongoDB if it doesn't exist,
        or retrieves the existing campaign with the same name.
        """
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
        """
        Called when a test suite starts.
        
        Args:
            data: Robot Framework suite data object.
            result: Robot Framework suite result object.
        """
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
        """
        Called when a test case starts.
        
        Args:
            data: Robot Framework test data object.
            result: Robot Framework test result object.
        """
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
        """
        Called when a keyword starts.
        
        Args:
            data: Robot Framework keyword data object.
            result: Robot Framework keyword result object.
        """
        if not self.current_test:
            return
        
        keyword_info = {
            'test_id': self.current_test['_id'],
            'name': getattr(data, 'kwname', None) or getattr(data, 'name', 'Unknown'),
            'library': getattr(data, 'libname', ''),
            'start_time': datetime.datetime.now()
        }
        
        self.connection.keywords.insert_one(keyword_info)
    
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
        
        Updates the campaign end timestamp and closes the MongoDB connection.
        """
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
