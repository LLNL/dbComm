import bson


def ObjectId(id):
    """Return a given id as an ObjectId

       Parameters:
           id: id (of a file record)

       Return:
           ObjectId
       """
    return bson.objectid.ObjectId(id)
