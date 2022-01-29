from googletrans import Translator
import duden
import databaseManager as db


def dudenCheck(name):
    checkWord = duden.get(name)

    if checkWord is None:
        checkWord = duden.get(name.capitalize())

    if checkWord is None:
        checkWord = duden.search(name)
    if checkWord is None:
        checkWord = duden.search(name.capitalize())

    return checkWord


def translate(name, destination, source):
    translator = Translator()
    translatedWord = translator.translate(text=name, dest=destination, src=source).text
    return translatedWord


class ChangeableVariables():
    def __init__(self, menuState):
        self.menuState: bool = menuState  # Store = false | learn = true
        self.questionsForLearnModule = []
        self.activeQuestion = []
        self.questionCount: int = 0
        self.learnDirection: str = "unset"

    def setLearnDirection(self, direction):
        self.learnDirection = direction
        return self.learnDirection

    def getLearnDirection(self):
        return self.learnDirection

    def getMenuState(self):
        return self.menuState

    def setMenuState(self, value):
        self.menuState = value
        return self.menuState

    def getGermanQuestionForLearn(self):  # returns the list within the questions for learn
        # if not self.questionsForLearnModule:
        questionList = db.DatabaseManager()
        if self.questionsForLearnModule:
            self.questionsForLearnModule.clear()
        self.questionsForLearnModule = questionList.getGermanDocument()
        return self.questionsForLearnModule

    def getEnglishQuestionForLearn(self):  # returns the list within the questions for learn
        # if not self.questionsForLearnModule:
        questionList = db.DatabaseManager()
        if self.questionsForLearnModule:
            self.questionsForLearnModule.clear()
        self.questionsForLearnModule = questionList.getEnglishDocument()
        return self.questionsForLearnModule

    def clearEntrys(self):
        self.questionsForLearnModule.clear()
        self.activeQuestion.clear()
        self.learnDirection = "unset"

    def setQuestionForLearn(self, questionList):
        self.questionsForLearnModule = questionList
        return self.questionsForLearnModule

    def getActiveQuestion(self):
        return self.activeQuestion

    def setActiveQuestion(self, randomVar):
        if self.activeQuestion:
            self.activeQuestion.clear()
        self.activeQuestion.append(self.questionsForLearnModule.pop(randomVar))
        return self.activeQuestion

    def getQuestionCount(self):
        return int(self.questionCount)

    def setQuestionCount(self, count):
        self.questionCount = count
        return self.questionCount
