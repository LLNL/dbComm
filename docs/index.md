# dbComm

dbComm is a wrapper for pymongo that simplifies MongoDB database interactions with support for SSH tunneling and LDAP authentication.

## Installation

```bash
pip install dbComm
```

## Quick Start

```python
from dbComm import Mongo

# Direct connection
db = Mongo(host="localhost", port=27017)

# SSH tunnel connection
db = Mongo(
    host="remote.server",
    port=27017,
    ssh=True,
    ssh_host="gateway.server",
    database="mydb"
)

# LDAP authentication
db = Mongo(
    host="mongodb.server",
    authentication="LDAP"
)
```

## Authentication Methods

### Direct Connection
Basic MongoDB connection without authentication:
```python
db = Mongo(host="localhost")
```

### SSH Tunnel
Connect through an SSH tunnel:
```python
db = Mongo(
    host="internal.server",
    ssh=True,
    ssh_host="gateway.server",
    ssh_username="user",
    database="mydb"
)
```

### LDAP Authentication
Connect using LDAP credentials:
```python
db = Mongo(
    host="mongodb.server",
    authentication="LDAP",
    username="ldap_user"
)
```

## API Reference

### Mongo Class

#### Constructor Parameters

- `host` (str): MongoDB server hostname
- `port` (int, optional): MongoDB port number. Default: 27017
- `authentication` (str, optional): Authentication type ('LDAP'). Default: None
- `username` (str, optional): Username for authentication
- `password` (str, optional): Password for authentication
- `ssh` (bool, optional): Use SSH tunnel. Default: False
- `ssh_host` (str, optional): SSH gateway server
- `database` (str, optional): Database name
- `ssh_username` (str, optional): SSH username
- `ssh_password` (str, optional): SSH password
- `timeout` (int, optional): Connection timeout in ms. Default: 5000

#### Methods

##### Database Operations

- `getDBs() -> List[str]`
  Returns list of available databases

- `setDB(db_name: str)`
  Connect to specific database

##### Record Operations

- `getRecord(collection: str, field: Union[str, ObjectId, Dict])`
  Retrieve single record from collection

- `getRecords(collection: str) -> List`
  Retrieve all records from collection

- `newRecord(collection: str, **kwargs) -> ObjectId`
  Create new record in collection

- `updateRecord(collection: str, field: Union[str, ObjectId, Dict], updateVals: Dict, updateType: str)`
  Update existing record

- `deleteRecords(collection: str)`
  Delete all records in collection

- `dropCollection(collection: str)`
  Delete entire collection

##### File Operations

- `putFile(filepath: str, **kwargs) -> ObjectId`
  Store file in GridFS

- `getFile(fileID: Union[str, ObjectId]) -> bytes`
  Retrieve file from GridFS

- `deleteFile(fileID: Union[str, ObjectId])`
  Delete file from GridFS

## Error Handling

The package raises standard MongoDB exceptions plus:

- `ValueError`: Invalid database or collection names
- `TypeError`: Invalid field types
- `Exception`: Connection timeouts

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License
see [LICENSE](LICENSE)