# Instructions for Setting Up dbComm
## Installing
Pip: `pip install git+https://mybitbucket.llnl.gov/scm/prec/database-comm.git`


URL: https://mybitbucket.llnl.gov/scm/prec/database-comm.git

Description: dbComm.py is a module for integrating a Python codebase with MongoDB using the PyMongo library.
The methods contained are used to connect to a Mongo database and push/pull data.

Requirements: PyMongo (and its companions GridFS and BSON) 

Usage:
To use dbComm, create an instance of the class. This will attempt to connect to the database. ***include details about URI and OUN/AD***
Upon successful connection, any of the methods can be used in the class to interact with the database.

## Troubleshooting
If when running the pip install, you get an error like `AttributeError: module 'enum' has no attribute 'IntFlag'` (32-bit Python), 
run: `pip uninstall enum34`