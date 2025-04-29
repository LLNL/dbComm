# API Reference

## Mongo Class

Provides an interface to MongoDB with support for SSH tunneling and LDAP authentication.

### Class Attributes

- `timeout` (int): Connection timeout in milliseconds
- `server` (SSHTunnelForwarder): SSH tunnel connection if active
- `username` (str): Current username for authentication
- `dbClient` (MongoClient): MongoDB client connection
- `db` (Database): Current active database
- `fs` (GridFS): GridFS instance for file operations
- `dbList` (List[str]): List of available databases
- `collList` (List[str]): List of collections in current database

### Constructor

```python
def __init__(
    self,
    host: str,
    port: int = 27017,
    authentication: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    ssh: bool = False,
    ssh_host: Optional[str] = None,
    database: Optional[str] = None,
    ssh_username: Optional[str] = None,
    ssh_password: Optional[str] = None,
    timeout: int = 5000,
):
```

Establishes connection to a MongoDB server based on provided parameters.

### Connection Methods

#### _connect_directly
```python
def _connect_directly(self, uri: str) -> None:
```
Internal method to establish direct MongoDB connection.

#### _connect_via_ssh
```python
def _connect_via_ssh(
    self,
    host: str,
    port: int,
    ssh_host: str,
    ssh_username: Optional[str],
    ssh_password: Optional[str],
    database: Optional[str],
    username: str,
    password: str,
) -> None:
```
Internal method to establish MongoDB connection through SSH tunnel.

#### _connect_with_ldap
```python
def _connect_with_ldap(
    self,
    host: Union[str, List[str]],
    port: int,
    password: Optional[str]
) -> None:
```
Internal method to establish MongoDB connection using LDAP authentication.

### Database Operations

#### getDBs
```python
def getDBs(self) -> List[str]:
```
Returns list of available databases on the server.

#### setDB
```python
def setDB(self, db_name: str) -> None:
```
Connects to a specific database and initializes GridFS.

### Record Operations

#### getRecord
```python
def getRecord(
    self,
    collection: str,
    field: Union[str, ObjectId, Dict]
) -> Dict:
```
Retrieves a single record from the specified collection.

#### getRecords
```python
def getRecords(self, collection: str) -> List[Dict]:
```
Retrieves all records from the specified collection.

#### newRecord
```python
def newRecord(self, collection: str, **kwargs) -> ObjectId:
```
Creates a new record in the specified collection with optional fields.

#### updateRecord
```python
def updateRecord(
    self,
    collection: str,
    field: Union[str, ObjectId, Dict],
    updateVals: Dict,
    updateType: str
) -> None:
```
Updates an existing record. UpdateType must be 'set' or 'push'.

#### deleteRecords
```python
def deleteRecords(self, collection: str) -> None:
```
Deletes all records in the specified collection.

#### dropCollection
```python
def dropCollection(self, collection: str) -> None:
```
Deletes the specified collection entirely.

### File Operations (GridFS)

#### putFile
```python
def putFile(self, filepath: str, **kwargs) -> ObjectId:
```
Stores a file in GridFS with optional metadata.

#### getFile
```python
def getFile(self, fileID: Union[str, ObjectId]) -> bytes:
```
Retrieves a file from GridFS by its ID.

#### deleteFile
```python
def deleteFile(self, fileID: Union[str, ObjectId]) -> None:
```
Deletes a file from GridFS by its ID.

### Helper Methods

#### _validate_field
```python
def _validate_field(
    self,
    field: Union[str, ObjectId, Dict]
) -> Dict:
```
Internal method to validate and normalize field parameters.

### Exceptions

- `ValueError`: Raised for invalid database names, collection names, or update types
- `TypeError`: Raised for invalid field types or parameters
- `pymongo.errors.ServerSelectionTimeoutError`: Raised for connection timeouts
- `Exception`: Generic exceptions with descriptive messages

### Type Hints

The package uses the following type hints:
```python
from typing import Dict, List, Optional, Union
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder
from pymongo.database import Database
from gridfs import GridFS
```