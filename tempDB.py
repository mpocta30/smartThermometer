import json

from pymongo import MongoClient, ASCENDING

class tempDB:
    def __init__(self, database, temps, read):
        client = MongoClient("mongodb://127.0.0.1:27017") #host uri
        db = client[database] #Select the database
        self.temps = db[temps] #Select the collection name
        self.read = db[read]



    # Find data in database within date range
    def find_byDate(self, date1, date2=None):
        if date2 == None:
            return self.temps.find({"time":{"$gte":date1}}).sort("time",ASCENDING)
        else:
            return self.temps.find({"time":{"$gte":date1,
                                        "$lt": date2}}).sort("time",ASCENDING)


    # Retrieve all data in the database
    def findAll(self):
        return self.temps.find({}).sort("time",ASCENDING)


    # Insert the new temperature values
    def insertTemp(self, time, cTemp, fTemp):
        self.temps.insert({"time": time, "ftemp": fTemp, "ctemp": cTemp})


    # Delete all documents in collection
    def clearCollection(self, collection):
        collection.remove()


    # Get read value
    def getRead(self):
        read = self.read.find({'name': 'read'})
        return read[0]['temp_read']


    # Update read value
    def updateRead(self, readBool):
        myQuery = {'name': 'read'}
        newValues = {'$set': {'temp_read': readBool}}
        
        self.read.update(myQuery, newValues)


    # Get the current alert threshold data
    def getAlert(self):
        read = self.read.find({'name': 'read'})
        return read[0]


    # Update current alert values
    def updateAlert(self, newValues):
        myQuery = {'name': 'read'}

        self.read.update(myQuery, newValues)

    