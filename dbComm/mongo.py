import datetime
from getpass import getpass, getuser
from typing import Dict, List, Optional, Union
from sshtunnel import SSHTunnelForwarder
import pymongo
import gridfs
from bson.objectid import ObjectId


class Mongo:
    """Provide an interface to MongoDB."""

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
        """Establish connection to a MongoDB server."""
        self.timeout = timeout
        self.server = None
        self.username = username or getuser()

        if "mongodb://" in host:
            self._connect_directly(host)
        elif ssh:
            self._connect_via_ssh(
                host,
                port,
                ssh_host,
                ssh_username,
                ssh_password,
                database,
                username,
                password,
            )
        elif authentication == "LDAP":
            self._connect_with_ldap(host, port, password)
        else:
            self._connect_directly(f"{host}:{port}")

    def _connect_directly(self, uri: str):
        """Connect directly to MongoDB."""
        try:
            self.dbClient = pymongo.MongoClient(
                uri, serverSelectionTimeoutMS=self.timeout
            )
            self.getDBs()
        except pymongo.errors.ServerSelectionTimeoutError:
            raise Exception("Server timeout. Check connection details.")

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
    ):
        """Connect to MongoDB via SSH."""
        ssh_username = ssh_username or input("LC Username: ")
        ssh_password = ssh_password or getpass("LC Password (VPN/CZ PIN + Token): ")
        self.server = SSHTunnelForwarder(
            (ssh_host, 22),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=(host, port),
            allow_agent=False,
        )
        self.server.start()
        self.dbClient = pymongo.MongoClient(
            f"mongodb://{username}:{password}@127.0.0.1/{database}?ssl=true&tlsAllowInvalidCertificates=true",
            port=self.server.local_bind_port,
        )
        self.getDBs()

    def _connect_with_ldap(
        self, host: Union[str, List[str]], port: int, password: Optional[str]
    ):
        """Connect to MongoDB using LDAP authentication."""
        if not password:
            password = getpass("Enter AD: ")
        uri = self._build_ldap_uri(host, port, password)
        self._connect_directly(uri)

    def _build_ldap_uri(
        self, host: Union[str, List[str]], port: int, password: str
    ) -> str:
        """Build the LDAP connection URI."""
        if isinstance(host, list):
            host = ",".join(f"{h}:{port}" for h in host)
        return f"mongodb://{self.username}:{password}@{host}/?authMechanism=PLAIN&replicaSet=ame&authSource=%24external&ssl=true"

    def getDBs(self) -> List[str]:
        """Get list of databases on the server."""
        self.dbList = self.dbClient.list_database_names()
        return self.dbList

    def setDB(self, db_name: str):
        """Connect to a specific database."""
        if db_name in self.dbList:
            self.db = self.dbClient[db_name]
            self.fs = gridfs.GridFS(self.db)
            self.collList = self.db.list_collection_names()
        else:
            raise ValueError(f"{db_name} is not one of the databases on the server.")

    def _validate_field(self, field: Union[str, ObjectId, Dict]) -> Dict:
        """Validate and normalize the field parameter."""
        if isinstance(field, (str, ObjectId)):
            return {"_id": ObjectId(field)}
        elif isinstance(field, dict):
            return field
        else:
            raise TypeError(
                "Invalid field. Must be either an ObjectId or a dictionary."
            )

    """
    This Section is actions on ALL collections
    """

    def getDBRecByID(self, RecID):
        """Search all collections for a record _id

        Parameters:
            RecID: the _id of the desired record

        Return:
            fColl: collection the record was found in
            fRec: record corresponding to the _id"""
        fColl, fRec = None, None
        for x in self.collList:
            coll = self.db[f"{x}"]
            rec = coll.find_one({"_id": ObjectId(RecID)})
            if rec:
                fColl = x
                fRec = rec
        return fColl, fRec

    def getData4Field(self, field):
        """Search all collections for a provided field

        Parameters:
            field: dict of key to search collections for

        Return:
            retList: list of the records with the matching field"""
        if type(field) is not dict:
            Exception("search field must be type <dict>")
        else:
            retList = list()
            if "system.profile" in self.collList:
                self.collList.remove("system.profile")
            for x in self.collList:
                coll = self.db[f"{x}"]
                for rec in coll.find(field):
                    retList.append({coll.name: rec})
            return retList

    """
    This Section is actions on records in a specified collection
    """

    def getRecord(self, collection, field):
        """Get a record given its collection and _id

        Parameters:
            collection: the collection of the desired record
            field: the _id or a key-value identifier of the desired record

        Return:
            retRec: the record corresponding to the recID"""

        if type(field) is str or type(field) is ObjectId:
            field = {"_id": ObjectId(field)}
        elif type(field) is not dict:
            raise Exception("Invalid field. Must be either an ObjectId or a dictionary")

        if collection in self.collList:
            retRec = self.db[collection].find_one(field)
        else:
            retRec = None
            print(
                "the collection '"
                + collection
                + "' does not exist in the database "
                + str(self.db.name)
            )
        return retRec

    def getRecords(self, collection):
        """Get all records in a collection

        Parameters:
            collection: the collection of the desired record

        Return:
            retStr: list of the records in the collection"""
        retStr = list()
        if collection in self.collList:
            for x in self.db[collection].find():
                retStr.append(x)
        else:
            print(
                "the collection '"
                + collection
                + "' does not exist in the database "
                + str(self.db.name)
            )
        return retStr

    def newRecord(self, collection, **kwargs):
        """Create a record in a given collection (with optional contents)

        Parameters:
            collection: the collection of the desired record
            kwargs (optional): key-value pairs of data to add to the record

        Return:
            _id of created record
        """

        newRec = {
            "userName": self.username,
            "CreateTime": datetime.datetime.now(),
        }
        newRec.update(kwargs)
        docID = self.db[collection].insert_one(newRec)
        return docID.inserted_id

    def updateRecord(
        self,
        collection: str,
        field: Union[str, ObjectId, Dict],
        updateVals: Dict,
        updateType: str,
    ):
        """Update a record in the database."""
        field = self._validate_field(field)
        if updateType == "set":
            self.db[collection].update_one(field, {"$set": updateVals})
        elif updateType == "push":
            self.db[collection].update_one(field, {"$push": updateVals})
        else:
            raise ValueError("Invalid updateType. Must be 'set' or 'push'.")

    def deleteRecords(self, collection):
        """Delete all records in a given collection

        Parameters:
            collection: the collection to be cleared

        Return:
            None
        """
        if collection in self.collList:
            x = collection.delete_many({})
            print(x.deleted_count, " documents deleted.")
        else:
            print(
                "the collection '"
                + collection
                + "' does not exist in the database "
                + str(self.db.name)
            )

    def dropCollection(self, collection):
        """Delete a given collection

        Parameters:
            collection: the collection to be deleted

        Return:
            None
        """
        x = collection.drop()
        if x:
            print(collection + " collection dropped successfully")
        else:
            print(
                "the collection '"
                + collection
                + "' does not exist in the database "
                + str(self.db.name)
            )

    """
    Methods for handling files in the database with gridFS
    """

    def putFile(self, filepath, **kwargs):
        """Put a file in GridFS storage

        Parameters:
            filepath: path to the file to be uploaded
            kwargs (optional): additional fields to be added to the record

        Return:
            _id of the file record
        """
        return self.fs.put(filepath, **kwargs)

    def getFile(self, fileID):
        """Get a file from GridFS storage

        Parameters:
            fileID: _id of the file record

        Return:
            the file corresponding to the _id (as returned by its .read() function)
        """
        if type(fileID) is str:
            fileID = ObjectId(fileID)
        return self.fs.get(fileID).read()

    def deleteFile(self, fileID):
        """Delete a file from GridFS storage

        Parameters:
            fileID: _id of the file record

        Return:
            None
        """
        self.fs.delete(fileID)

    def stop(self):
        """If an SSH connection is done, this is required to stop the connection."""
        if self.server:
            self.server.stop()


if __name__ == "__main__":
    db = Mongo("localhost")
    print(db.getDBs())
    db.stop()
