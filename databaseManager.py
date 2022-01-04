from pymongo import MongoClient

client = MongoClient(port=27017)
db=client["vocabularydatabase"]

class DatabaseManager():
    def __init__(self, id, deutsch, englisch, gelernt):
        self.id = id
        self.deutsch = deutsch
        self.englisch = englisch
        self.gelernt = gelernt
        self.dbColGerToEng = db["GermanToEnglish"]
        #self.dbColEngToGer = db["EnglishToGerman"]


    def createInstanceGerToEng(self):
        nameDoc = {
            'id': self.id,
            'deutsch': self.deutsch,
            'englisch': self.englisch,
            'gelernt': self.gelernt
        }
        x = self.dbColGerToEng.insert_one(nameDoc)

    def getDocument(self):
        documents = self.dbColGerToEng.find()
        for x in documents:
            print(x)

        return documents

