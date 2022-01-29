from pymongo import MongoClient

client = MongoClient(port=27017)
db=client["vocabularydatabase"]

questionsLearnModule = []

class DatabaseManager():
    def __init__(self, id = 0, firstWord = "", secondWord = "", gelernt = ""):
        self.id = id
        self.firstWord = firstWord
        self.secondWord = secondWord
        self.gelernt = gelernt
        self.dbColGerToEng = db["GermanToEnglish"]
        self.dbColEngToGer = db["EnglishToGerman"]



    def createInstanceGerToEng(self):
        nameDoc = {
            'id': self.id,
            'deutsch': self.firstWord,
            'englisch': self.secondWord,
            'gelernt': self.gelernt
        }
        x = self.dbColGerToEng.insert_one(nameDoc)

    def createInstanceEngToGer(self):
        nameDoc = {
            'id': self.id,
            'englisch': self.firstWord,
            'deutsch': self.secondWord,
            'gelernt': self.gelernt
        }
        x = self.dbColEngToGer.insert_one(nameDoc)

    def getGermanDocument(self):
        documents = self.dbColGerToEng.find()
        if questionsLearnModule:
            questionsLearnModule.clear()
        for x in documents:
            questionsLearnModule.append(dict(x))
            print(x)
        return questionsLearnModule

    def getEnglishDocument(self):
        documents = self.dbColEngToGer.find()
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
