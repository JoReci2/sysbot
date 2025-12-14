# Database Listener Plugin

A Robot Framework listener plugin that stores test execution results in various databases using SQLAlchemy for SQL databases.

## Supported Databases

- **SQLite** - File-based database
- **MySQL** - Relational database
- **PostgreSQL** - Advanced relational database
- **MongoDB** - NoSQL document database

## Installation

### Using pip with extras

```bash
# Install with all database support
pip install sysbot[all_databases]

# Or install with specific database support
pip install sysbot[mysql]
pip install sysbot[postgresql]
pip install sysbot[mongodb]
```

### Manual Installation

```bash
# Core requirement: SQLAlchemy for SQL databases
pip install sqlalchemy

# For MySQL support
pip install mysql-connector-python

# For PostgreSQL support
pip install psycopg2-binary

# For MongoDB support
pip install pymongo
```

## Usage

The listener can be used with Robot Framework's `--listener` option:

```bash
robot --listener sysbot.plugins.listener.DatabaseListener:db_type:connection_string:campaign_name tests/
```

### SQLite Examples

```bash
# Store results in results.db file with campaign name
robot --listener sysbot.plugins.listener.DatabaseListener:sqlite:results.db:MyCampaign tests/

# Store results in /tmp/test_results.db
robot --listener sysbot.plugins.listener.DatabaseListener:sqlite:/tmp/test_results.db:MyProject tests/
```

### MySQL Examples

```bash
# Connect to MySQL database
robot --listener sysbot.plugins.listener.DatabaseListener:mysql:mysql://user:password@localhost/testdb:MyCampaign tests/

# With custom port
robot --listener sysbot.plugins.listener.DatabaseListener:mysql:mysql://user:password@localhost:3307/testdb:MyCampaign tests/
```

### PostgreSQL Examples

```bash
# Connect to PostgreSQL database
robot --listener sysbot.plugins.listener.DatabaseListener:postgresql:postgresql://user:password@localhost/testdb:MyCampaign tests/

# With custom port
robot --listener sysbot.plugins.listener.DatabaseListener:postgresql:postgresql://user:password@localhost:5433/testdb:MyCampaign tests/
```

### MongoDB Examples

```bash
# Connect to MongoDB database
robot --listener sysbot.plugins.listener.DatabaseListener:mongodb:mongodb://localhost:27017/testdb:MyCampaign tests/

# With authentication
robot --listener sysbot.plugins.listener.DatabaseListener:mongodb:mongodb://user:password@localhost:27017/testdb:MyCampaign tests/
```

## Database Schema

### SQL Databases (SQLite, MySQL, PostgreSQL)

The listener creates a hierarchical structure with four tables:

#### test_campaigns
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| name | VARCHAR(500) | Campaign name |
| start_time | TIMESTAMP | Campaign start time |
| end_time | TIMESTAMP | Campaign end time |
| description | TEXT | Campaign description |

#### test_suites
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| campaign_id | INTEGER | Foreign key to test_campaigns |
| name | VARCHAR(500) | Suite name |
| doc | TEXT | Suite documentation |
| start_time | TIMESTAMP | Suite start time |
| end_time | TIMESTAMP | Suite end time |
| status | VARCHAR(50) | Suite status (PASS/FAIL) |
| message | TEXT | Suite message |
| metadata | TEXT | Suite metadata (JSON) |

#### test_cases
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| suite_id | INTEGER | Foreign key to test_suites |
| name | TEXT | Test case name |
| doc | TEXT | Test case documentation |
| tags | TEXT | Test case tags (comma-separated) |
| start_time | TIMESTAMP | Test start time |
| end_time | TIMESTAMP | Test end time |
| status | TEXT | Test status (PASS/FAIL) |
| message | TEXT | Test message |

#### keywords
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER/SERIAL | Primary key |
| test_id | INTEGER | Foreign key to test_cases |
| name | TEXT | Keyword name |
| library | TEXT | Library name |
| start_time | TIMESTAMP | Keyword start time |
| end_time | TIMESTAMP | Keyword end time |
| status | TEXT | Keyword status |
| message | TEXT | Keyword message |

### MongoDB

The listener creates three collections with similar structure:
- `test_suites`
- `test_cases`
- `keywords`

## Querying Results

### SQLite

```bash
# View all test suites
sqlite3 results.db "SELECT * FROM test_suites;"

# View all test cases with their status
sqlite3 results.db "SELECT name, status, start_time, end_time FROM test_cases;"

# Count tests by status
sqlite3 results.db "SELECT status, COUNT(*) FROM test_cases GROUP BY status;"

# View failed tests
sqlite3 results.db "SELECT name, message FROM test_cases WHERE status='FAIL';"
```

### MySQL

```sql
-- Connect to database
mysql -u user -p testdb

-- View all test cases
SELECT name, status, start_time, end_time FROM test_cases;

-- Get test statistics
SELECT status, COUNT(*) as count FROM test_cases GROUP BY status;
```

### PostgreSQL

```sql
-- Connect to database
psql -U user -d testdb

-- View all test cases
SELECT name, status, start_time, end_time FROM test_cases;

-- Get test duration
SELECT name, (end_time - start_time) as duration FROM test_cases;
```

### MongoDB

```javascript
// Connect to MongoDB
mongo testdb

// View all test cases
db.test_cases.find()

// Get test statistics
db.test_cases.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])

// View failed tests
db.test_cases.find({ status: "FAIL" })
```

## Notes

- The database and tables/collections are created automatically if they don't exist using SQLAlchemy
- SQL databases use SQLAlchemy ORM for better maintainability and database portability
- MongoDB doesn't require schema initialization
- Connection errors are raised at listener initialization with clear dependency installation instructions
- The listener automatically closes database connections when tests complete

## Architecture

- **SQL Databases (SQLite, MySQL, PostgreSQL)**: Uses SQLAlchemy for database abstraction and ORM
- **MongoDB**: Uses pymongo driver directly for NoSQL operations

## Error Handling

If a database connection fails, the listener will raise an exception with details:
- For missing dependencies (SQLAlchemy, database drivers), it will suggest the required package to install
- For connection errors, it will provide the error message from the database driver

## License

This plugin is part of the SysBot project and follows the same MIT License.
