# dbComm

[![PyPi](https://img.shields.io/pypi/v/hy.svg)](https://pypi.org/project/dbComm/)

- **Author:** Pigeon Caviness ([caviness2@llnl.gov](mailto:caviness2@llnl.gov))

## About
dbComm is a module for integrating a Python codebase with MongoDB using the PyMongo library.
The methods contained are used to connect to a Mongo database and push/pull data.

## Installing
The easiest method of installation is through using Pip. <br>
`pip install -U git+https://github.com/LLNL/dbComm.git`

If you prefer, you can clone the repo using:<br>
`git clone https://github.com/LLNL/dbComm.git`

## Usage
To use dbComm, create an instance of the class. This will attempt to connect to the database.
Upon successful connection, any of the methods can be used in the class to interact with the database.
```
import dbComm
db = dbComm.Mongo('myServer')
print(myServer.getDBs())
```

## Troubleshooting
If when running the pip install, you get an error like `AttributeError: module 'enum' has no attribute 'IntFlag'` 
(32-bit Python),<br> 
run: `pip uninstall enum34`

## Contributing
dbComm is an open source project and constantly evolving! 
We welcome contributions via pull requests as well as questions, feature requests, or bug reports via issues. 
Contact our team at caviness2@llnl.gov with any questions. <br><br>
If you are not a developer at LLNL, you won't have permission to push new branches to the repository. 
First, you should create a fork. 
This will create your copy of the ATS repository and ensure you can push your changes up to GitHub and create PRs.

## License
LLNL-CODE-845190<br>
<!---SPDX-License-Identifier: MIT-->