# dbComm
- **Author:** Alex Caviness ([caviness2@llnl.gov](mailto:caviness2@llnl.gov))
- **Source code:** https://mybitbucket.llnl.gov/projects/LLNL/repos/database-comm/

## About
dbComm is a module for integrating a Python codebase with MongoDB using the PyMongo library.
The methods contained are used to connect to a Mongo database and push/pull data.

## Installing
The easiest method of installation is through using Pip. <br>
`pip install git+https://mybitbucket.llnl.gov/scm/llnl/database-comm.git`

If you prefer, you can clone the repo using:<br>
`git clone https://mybitbucket.llnl.gov/scm/llnl/database-comm.git dbComm`

## Usage
To use dbComm, create an instance of the class. This will attempt to connect to the database.
Upon successful connection, any of the methods can be used in the class to interact with the database.
```
import dbComm as db
ammoDB = db.Mongo('maptac19')
print(ammoDB.getDBs())
```

## Troubleshooting
If when running the pip install, you get an error like `AttributeError: module 'enum' has no attribute 'IntFlag'` (32-bit Python),<br> 
run: `pip uninstall enum34`