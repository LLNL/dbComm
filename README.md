# dbComm

A Python wrapper for pymongo with support for SSH tunneling and LDAP authentication.

## Features

- Simple MongoDB connection interface
- SSH tunnel support
- LDAP authentication
- GridFS file operations
- Comprehensive type hints

## Installation

```bash
pip install dbComm
```

## Quick Usage

```python
from dbComm import Mongo

# Connect to database
db = Mongo(host="localhost")
db.setDB("mydatabase")

# Create record
record_id = db.newRecord("mycollection", field1="value1", field2="value2")

# Retrieve record
record = db.getRecord("mycollection", record_id)
```

## Documentation

For full documentation, visit [docs/index.md](docs/index.md)

## License
see [LICENSE](LICENSE.md)