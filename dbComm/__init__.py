"""**dbComm** is a wrapper for pymongo."""

from .mongo import Mongo
from bson.objectid import ObjectId

__all__ = [
    "Mongo",
    "ObjectId",
]
