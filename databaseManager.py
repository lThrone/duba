from pymongo import MongoClient

client = MongoClient(port=27017)
db=client["vocabularydatabase"]

questionsLearnModule = []

class DatabaseManager():
    def __init__(self, id = 0, deutsch = "", englisch = "", gelernt = ""):
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
        if questionsLearnModule:
            questionsLearnModule.clear()
        for x in documents:
            questionsLearnModule.append(dict(x))
            print(x)
        return questionsLearnModule

    def deleteEntrys(self):
        query = {"deutsch": {"$regex": "*"}} # remove filter
        d = self.dbColGerToEng.delete_many({})
        print(d.deleted_count, " documents deleted !!")
