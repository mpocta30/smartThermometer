import json

from pymongo import MongoClient, ASCENDING

class tempDB:
    def __init__(self, database, collection):
        client = MongoClient("mongodb://127.0.0.1:27017") #host uri
        db = client[database] #Select the database
        self.collection = db[collection] #Select the collection name

    def find_byDate(self, date1, date2=None):
        if date2 == None:
            return self.collection.find({"time":{"$gte":date1}}).sort("time",ASCENDING)
        else:
            return self.collection.find({"time":{"$gte":date1,
                                        "$lt": date2}}).sort("time",ASCENDING)

    def findAll(self):
        return self.collection.find({}).sort("time",ASCENDING)


    