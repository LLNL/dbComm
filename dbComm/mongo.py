# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
import bson
import datetime
import gridfs
import pymongo
from getpass import getpass, getuser
import sys
from sshtunnel import SSHTunnelForwarder


class Mongo:
    """Provide an interface to MongoDB."""

    def __init__(
        self,
        host,
        port=27017,
        authentication=None,
        username=None,
        password=None,
        ssh=False,
        ssh_host=None,
        database=None,
        timeout=5000,
    ):
        """Establish connection to a MongoDB server.

        The `host` parameter can be a full `mongodb URI
        <http://dochub.mongodb.org/core/connections>`_, in addition to
        a simple hostname.

        Parameters:
          - host: hostname or IP address, or a
            mongodb URI.
          - port (optional): port number on which to connect
          - authentication (optional): type of authentication
          - username (optional): username to connect to DB
          - password (optional): password to connect to DB
        """

        self.timeout = timeout
        self.server = None
        if username:
            self.username = username
        else:
            self.username = getuser()
        if "mongodb://" in host:
            try:
                self.newConn(host)
            except pymongo.errors.ServerSelectionTimeoutError:
                raise Exception("Server timeout. Check connection details.")
        elif ssh == True:
            self.server = SSHTunnelForwarder(
                (ssh_host, 22),
                ssh_username=input("LC Username: "),
                ssh_password=getpass("LC Password (VPN/CZ PIN + Token): "),
                remote_bind_address=(host, port),
                allow_agent=False,
            )
            self.server.start()
            self.dbClient = pymongo.MongoClient(
                f"mongodb://{username}:{password}@127.0.0.1/{database}?ssl=true&tlsAllowInvalidCertificates=true",
                port=self.server.local_bind_port,
            )
            self.dbList = self.dbClient.list_database_names()
        elif authentication == None:
            try:
                self.newConn(f"{host}:{port}")
            except pymongo.errors.ServerSelectionTimeoutError:
                raise Exception("Server timeout. Check connection details.")
        elif authentication == "LDAP":
            auth = False
            # attempts = 0
            # while not auth:
            #     attempts += 1
            #     if attempts > 5:
            #         raise Exception('Too many failed password attempts.')
            #         break
            try:
                # to work in PyCharm, 'Edit Configurations' and tick the 'Emulate terminal' box
                # otherwise, the entered password will be printed to the console
                if password:
                    pass
                elif sys.stdin.isatty():
                    password = getpass("Enter AD: ")
                else:
                    print("Enter AD: ")
                    password = sys.stdin.readline().rstrip()
                if type(host) is list:
                    insert = ""
                    for h in host:
                        insert += f"{h}:{port},"
                    insert = insert[:-1]  # removes trailing comma
                    uri = f"mongodb://{self.username}:{password}@{insert}/?authMechanism=PLAIN&replicaSet=ame&authSource=%24external&ssl=true"
                else:
                    uri = (
                        f"mongodb://{self.username}:{password}@{host}:{port}/tls=true?authMechanism=PLAIN&"
                        "replicaSet=ame&readPreference=primary&authSource=%24external&directConnection=true&ssl=true"
                    )
                self.newConn(uri)
                auth = True
                print(f"Connected to {host}")
            except pymongo.errors.OperationFailure:  # Authentication Error
                print("Authentication Error. Try again.")
                password = None
            except pymongo.errors.ServerSelectionTimeoutError:
                raise Exception("Server timeout. Check connection details.")
        else:
            print("Authentication method not set up yet. Contact admin")

    """
    Connection block
    """

    def newConn(self, host):
        """Connect to database and establish collections

        Parameters:
            host: host:port or MongoDB URI

        Return:
            None"""

        self.dbClient = pymongo.MongoClient(host, serverSelectionTimeoutMS=self.timeout)
        self.getDBs()

    def getDBs(self):
        """Get list of databases on the server"""
        self.dbList = self.dbClient.list_database_names()
        return self.dbList

    def setDB(self, db_name):
        """Connect to different database on the server

        Parameters:
            db_name: name of the database on the server to switch to

        Return:
            None"""

        if db_name in self.dbList:
            self.db = self.dbClient[db_name]
            self.fs = gridfs.GridFS(self.db)
            self.collList = self.db.list_collection_names()
        else:
            print(db_name, "is not one of the databases on the server.")

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

        if type(field) is str or type(field) is bson.objectid.ObjectId:
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

    def updateRecord(self, collection, field, updateVals, updateType):
        """Update a record with a set of values given a collection and _id

        Parameters:
            collection: the collection of the desired record
            field: the _id or a key-value identifier of the desired record
            updateVals: a dict of the information to add to the DB record
            updateType: 'set' overrides the existing value if extant
                        'push' appends this entry to a list

        Return:
            None
        """
        if type(field) is str or type(field) is bson.objectid.ObjectId:
            field = {"_id": ObjectId(field)}
        elif type(field) is not dict:
            raise Exception("Invalid field. Must be either an ObjectId or a dictionary")

        if collection in self.collList:
            retRec = self.db[collection].find_one(field)
        if updateType == "set":  # overrides the values
            self.db[collection].update_one(field, {"$set": updateVals})
        elif updateType == "push":  # appends the values to an array
            self.db[collection].update_one(field, {"$push": updateVals})

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
