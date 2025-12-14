#!/usr/bin/env python3
"""
Example script to query test results from a SQLite database created by the DatabaseListener plugin.

Usage:
    python query_results.py results.db
"""

import sqlite3
import sys
from datetime import datetime


def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def query_suites(cursor):
    """Query and display test suite information."""
    print_header("Test Suites")
    cursor.execute("""
        SELECT id, name, status, start_time, end_time 
        FROM test_suites 
        ORDER BY start_time DESC
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("No test suites found.")
        return
    
    for row in rows:
        suite_id, name, status, start_time, end_time = row
        print(f"\nSuite ID: {suite_id}")
        print(f"  Name: {name}")
        print(f"  Status: {status}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")


def query_test_cases(cursor):
    """Query and display test case information."""
    print_header("Test Cases")
    cursor.execute("""
        SELECT tc.id, ts.name as suite_name, tc.name, tc.tags, tc.status, tc.start_time, tc.end_time
        FROM test_cases tc
        JOIN test_suites ts ON tc.suite_id = ts.id
        ORDER BY tc.start_time DESC
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("No test cases found.")
        return
    
    for row in rows:
        test_id, suite_name, name, tags, status, start_time, end_time = row
        print(f"\nTest ID: {test_id}")
        print(f"  Suite: {suite_name}")
        print(f"  Name: {name}")
        print(f"  Tags: {tags or 'None'}")
        print(f"  Status: {status}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")


def query_statistics(cursor):
    """Query and display test statistics."""
    print_header("Statistics")
    
    # Test case statistics
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM test_cases 
        GROUP BY status
    """)
    
    print("\nTest Cases by Status:")
    total = 0
    for row in cursor.fetchall():
        status, count = row
        print(f"  {status}: {count}")
        total += count
    print(f"  Total: {total}")
    
    # Suite statistics
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM test_suites 
        GROUP BY status
    """)
    
    print("\nTest Suites by Status:")
    for row in cursor.fetchall():
        status, count = row
        print(f"  {status}: {count}")


def query_failed_tests(cursor):
    """Query and display failed test cases."""
    print_header("Failed Tests")
    cursor.execute("""
        SELECT tc.name, tc.message, ts.name as suite_name
        FROM test_cases tc
        JOIN test_suites ts ON tc.suite_id = ts.id
        WHERE tc.status = 'FAIL'
        ORDER BY tc.start_time DESC
    """)
    
    rows = cursor.fetchall()
    if not rows:
        print("No failed tests found. All tests passed!")
        return
    
    for row in rows:
        name, message, suite_name = row
        print(f"\nTest: {name}")
        print(f"  Suite: {suite_name}")
        print(f"  Message: {message or 'No message'}")


def main():
    """Main function to run queries."""
    if len(sys.argv) < 2:
        print("Usage: python query_results.py <database_file>")
        sys.exit(1)
    
    db_file = sys.argv[1]
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Run all queries
        query_statistics(cursor)
        query_suites(cursor)
        query_test_cases(cursor)
        query_failed_tests(cursor)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
