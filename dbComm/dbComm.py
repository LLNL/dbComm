# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
from bson.binary import Binary
import bson
import datetime
import time
import gridfs
import io
import matplotlib.pyplot as plt
import pickle
from PIL import Image
import pymongo
import os
import getpass
import sys

class Mongo:
    """Provide interface to DB (currently MongoDB)."""

    def __init__(self, hostname, port=27017, authentication='None', OUN=None, AD=None, debug=False):
        """Establish connection to DB server."""
        self.debug = debug
        if self.debug:
            self.logFile = f'logs/dbCommLog_{round(time.time())}.txt'
            file = open(self.logFile, 'w+')
            file.close()

        if authentication == 'None':
            self.newConn(f'{hostname}:{port}')
            self.host = hostname
        elif authentication == 'LDAP':
            auth = False
            attempts = 0
            while not auth:
                attempts += 1
                if attempts > 5:
                    raise Exception('Too many failed password attempts.')
                    break
                try:
                    if OUN:
                        self.OUN = OUN
                    else:
                        self.OUN = getpass.getuser()
                    # to work in PyCharm, 'Edit Configurations' and tick the 'Emulate terminal' box
                    # otherwise, the entered password will be printed to the console
                    if AD:
                        pass
                    elif sys.stdin.isatty():
                        AD = getpass.getpass('Enter AD: ')
                    else:
                        print('Enter AD: ')
                        AD = sys.stdin.readline().rstrip()

                    self.host = hostname
                    uri = f'mongodb://{self.OUN}:{AD}@{self.host}:{port}/tls=true?authMechanism=PLAIN&' \
                      'replicaSet=ame&readPreference=primary&authSource=%24external&directConnection=true&ssl=true'
                    self.newConn(uri)
                    auth = True
                    print(f'Connected to {hostname}')
                except pymongo.errors.OperationFailure:  # Authentication Error
                    print('Authentication Error. Try again.')
                    AD = None
                except: # UNREACHABLE # if a connection to a remote server cannot be established, attempt to connect to localhost
                    auth = True
                    try:
                        self.newConn('localhost:27017')
                        self.host = 'localhost'
                        print('Connection to remote DB failed. Connected to localhost')
                    except:
                        self.host = 'NONE'
                        print('No DB available. See admin.')
        else:
            print('Authentication method not set up yet. Contact admin')

        if self.debug:
            with open(self.logFile, "w") as log:
                log.write(f'Host: {self.host}\n')

    '''
    Connection block
    '''
    def newConn(self, host):
        """Connect to database depending on debug and establish collections"""
        self.dbClient = pymongo.MongoClient(host, serverSelectionTimeoutMS=5000)
        self.getDBs()

    def getDBs(self):
        """Get list of databases on the server"""
        self.dbList = self.dbClient.list_database_names()
        return self.dbList

    def setDB(self, db_name):
        """Connect to different database on the server"""
        if db_name in self.dbList:
            self.db = self.dbClient[db_name]
            self.fs = gridfs.GridFS(self.db)
            self.collList = self.db.list_collection_names()
        else:
            print(db_name, 'is not one of the databases on the server.')

    '''
    This Section is actions on ALL collections
    '''
    def getDBRecByID(self, RecID):
        """Search all collections for a record _id"""
        fColl, fRec = None, None
        for x in self.collList:
            coll = self.db[f"{x}"]
            rec = coll.find_one({'_id': ObjectId(RecID)})
            if rec:
                fColl = x
                fRec = rec
        return fColl, fRec

    def getData4Field(self, field):
        """Search all collections for a provided field"""
        if type(field) is not dict:
            Exception('search field must be type <dict>')
        else:
            retList = list()
            if 'system.profile' in self.collList:
                self.collList.remove('system.profile')
            for x in self.collList:
                coll = self.db[f"{x}"]
                for rec in coll.find(field):
                    retList.append({coll.name: rec})
            return retList

    '''
    This Section is actions on records in a specified collection
    '''
    def getRecord(self, collection, recID):
        '''Get a record given its collection and _id '''
        if collection in self.collList:
            retRec = self.db[collection].find_one({"_id": ObjectId(recID)})
        else:
            retRec = None
            print('the collection \'' + collection + '\' does not exist in the database ' + str(self.db.name))
        return retRec

    def getRecords(self, collection):
        '''Get all records in a collection'''
        retStr = list()
        if collection in self.collList:
            for x in self.db[collection].find():
                retStr.append(x)
        else:
            print('the collection \'' + collection + '\' does not exist in the database ' + str(self.db.name))
        return retStr

    def updateRecord(self, collection, recID, updateVals, updateType):
        '''Update a record with a set of values given a collection and _id'''
        if updateType == 'set':  # overrides the values
            self.db[collection].update_one({'_id': ObjectId(recID)}, {'$set': updateVals})
        elif updateType == 'push':  # appends the values to an array
            self.db[collection].update_one({'_id': ObjectId(recID)}, {'$push': updateVals})

    def newRecord(self, collection, **kwargs):
        newRec = {
            "userName": self.OUN,
            "CreateTime": datetime.datetime.now(),
        }
        newRec.update(kwargs)
        docID = self.db[collection].insert_one(newRec)
        return docID.inserted_id

    def deleteRecords(self, collection):
        if collection in self.collList:
            x = collection.delete_many({})
            print(x.deleted_count, " documents deleted.")
        else:
            print('the collection \'' + collection + '\' does not exist in the database ' + str(self.db.name))

    def dropCollection(self, collection):
        x = collection.drop()
        if x:
            print(collection + ' collection dropped successfully')
        else:
            print('the collection \'' + collection + '\' does not exist in the database ' + str(self.db.name))\


    '''
    Methods for handling files in the database with gridFS
    '''
    def putFile(self, filepath, **kwargs):
        return self.fs.put(filepath, **kwargs)
    def getFile(self, fileID):
        return self.fs.get(fileID).read()
    def deleteFile(self, fileID):
        self.fs.delete(fileID)


if __name__ == "__main__":
    db = dbComm('wci-ame-u-prd.llnl.gov', authentication='LDAP')
    # db = dbComm('maptac19')
    print(db.getDBs())
    # print(db.getRecords(db.collList[0]))


