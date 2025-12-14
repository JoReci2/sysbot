#!/usr/bin/env python3
"""
Example script to query test results from a MongoDB database created by the DatabaseListener plugin.

Usage:
    python query_mongodb_results.py mongodb://localhost:27017/testdb
"""

import sys
try:
    from pymongo import MongoClient
except ImportError:
    print("Error: pymongo is required. Install it with: pip install pymongo")
    sys.exit(1)


def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def query_suites(db):
    """Query and display test suite information."""
    print_header("Test Suites")
    suites = db.test_suites.find().sort("start_time", -1)
    
    count = 0
    for suite in suites:
        count += 1
        print(f"\nSuite ID: {suite['_id']}")
        print(f"  Name: {suite['name']}")
        print(f"  Status: {suite.get('status', 'N/A')}")
        print(f"  Start: {suite.get('start_time', 'N/A')}")
        print(f"  End: {suite.get('end_time', 'N/A')}")
    
    if count == 0:
        print("No test suites found.")


def query_test_cases(db):
    """Query and display test case information."""
    print_header("Test Cases")
    
    # Join with suites to get suite names
    pipeline = [
        {
            "$lookup": {
                "from": "test_suites",
                "localField": "suite_id",
                "foreignField": "_id",
                "as": "suite"
            }
        },
        {"$sort": {"start_time": -1}}
    ]
    
    test_cases = db.test_cases.aggregate(pipeline)
    
    count = 0
    for test in test_cases:
        count += 1
        suite_name = test['suite'][0]['name'] if test.get('suite') and len(test['suite']) > 0 else 'Unknown'
        print(f"\nTest ID: {test['_id']}")
        print(f"  Suite: {suite_name}")
        print(f"  Name: {test['name']}")
        print(f"  Tags: {test.get('tags', 'None')}")
        print(f"  Status: {test.get('status', 'N/A')}")
        print(f"  Start: {test.get('start_time', 'N/A')}")
        print(f"  End: {test.get('end_time', 'N/A')}")
    
    if count == 0:
        print("No test cases found.")


def query_statistics(db):
    """Query and display test statistics."""
    print_header("Statistics")
    
    # Test case statistics
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    
    results = list(db.test_cases.aggregate(pipeline))
    
    if results:
        print("\nTest Cases by Status:")
        total = 0
        for result in results:
            status = result['_id'] or 'Unknown'
            count = result['count']
            print(f"  {status}: {count}")
            total += count
        print(f"  Total: {total}")
    else:
        print("\nNo test cases found.")
    
    # Suite statistics
    suite_results = list(db.test_suites.aggregate(pipeline))
    
    if suite_results:
        print("\nTest Suites by Status:")
        for result in suite_results:
            status = result['_id'] or 'Unknown'
            count = result['count']
            print(f"  {status}: {count}")


def query_failed_tests(db):
    """Query and display failed test cases."""
    print_header("Failed Tests")
    
    # Join with suites to get suite names
    pipeline = [
        {"$match": {"status": "FAIL"}},
        {
            "$lookup": {
                "from": "test_suites",
                "localField": "suite_id",
                "foreignField": "_id",
                "as": "suite"
            }
        },
        {"$sort": {"start_time": -1}}
    ]
    
    failed_tests = db.test_cases.aggregate(pipeline)
    
    count = 0
    for test in failed_tests:
        count += 1
        suite_name = test['suite'][0]['name'] if test.get('suite') and len(test['suite']) > 0 else 'Unknown'
        print(f"\nTest: {test['name']}")
        print(f"  Suite: {suite_name}")
        print(f"  Message: {test.get('message', 'No message')}")
    
    if count == 0:
        print("No failed tests found. All tests passed!")


def main():
    """Main function to run queries."""
    if len(sys.argv) < 2:
        print("Usage: python query_mongodb_results.py <mongodb_connection_string>")
        print("Example: python query_mongodb_results.py mongodb://localhost:27017/testdb")
        sys.exit(1)
    
    connection_string = sys.argv[1]
    
    try:
        client = MongoClient(connection_string)
        
        # Extract database name from connection string
        from urllib.parse import urlparse
        parsed = urlparse(connection_string)
        db_name = parsed.path.lstrip('/') if parsed.path else 'testdb'
        
        db = client[db_name]
        
        # Test connection
        client.server_info()
        
        # Run all queries
        query_statistics(db)
        query_suites(db)
        query_test_cases(db)
        query_failed_tests(db)
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
