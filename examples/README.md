# Examples

This directory contains example scripts for using the SysBot database listener plugin.

## Query Results Scripts

### SQLite Query Script

`query_results.py` - Query and display test results from SQLite databases

**Usage:**
```bash
python examples/query_results.py results.db
```

**Features:**
- Display test statistics (passed/failed counts)
- Show all test suites
- Show all test cases
- List failed tests with messages

### MongoDB Query Script

`query_mongodb_results.py` - Query and display test results from MongoDB databases

**Usage:**
```bash
python examples/query_mongodb_results.py mongodb://localhost:27017/testdb
```

**Features:**
- Display test statistics (passed/failed counts)
- Show all test suites
- Show all test cases
- List failed tests with messages

## Example Workflow

### 1. Run Tests with Database Listener

```bash
# SQLite example
robot --listener sysbot.plugins.listener.DatabaseListener:sqlite:results.db tests/

# MongoDB example
robot --listener sysbot.plugins.listener.DatabaseListener:mongodb:mongodb://localhost:27017/testdb tests/
```

### 2. Query Results

```bash
# For SQLite
python examples/query_results.py results.db

# For MongoDB
python examples/query_mongodb_results.py mongodb://localhost:27017/testdb
```

### 3. Export Results

```bash
# SQLite - Export to CSV
sqlite3 -header -csv results.db "SELECT * FROM test_cases;" > results.csv

# MongoDB - Export to JSON
mongoexport --db=testdb --collection=test_cases --out=results.json
```

## Dependencies

- **query_results.py**: No additional dependencies (uses built-in sqlite3)
- **query_mongodb_results.py**: Requires pymongo (`pip install pymongo`)
