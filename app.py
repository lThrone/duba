from flask import Flask
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
from alexa import data, util
import databaseManager as db
import random

app = Flask(__name__)

sb = SkillBuilder()

learnModeStatus = "inactive"
questionsForLearnModule = []
activeQuestion = []
dbGerToEng = db.DatabaseManager()
questionCount = 0
randomVariable = 0

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = data.WELCOME

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class AddVocabularyRequestHandler(AbstractRequestHandler):
    """Handler for option to add vocabulary"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AddVocabulary")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response


        speech_text = data.ADDQUESTLANGUAGEREQUESTMSG

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Vokabel hinzufügen", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class StoreVocabularyRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StoreVocabulary")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        val = slots["wordForTranslation"].value

        checkVoc = util.dudenCheck(val)
        print(checkVoc.name)

        translation = util.translate(val)
        print(translation)

        try:
            dbGerToEng = db.DatabaseManager(random.randint(1000, 9999), checkVoc.name, translation, False)
            dbGerToEng.createInstanceGerToEng()
            questionsForLearnModule = dbGerToEng.getDocument()
        except Exception as e:
            print(e)

        #for i in questionsForLearnModule:
        #    print(i)

        print(questionsForLearnModule[0])
        speech_text = data.STOREVOCABULARYSPEECHTEXT.format(checkword=checkVoc.name, transl=translation)


        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Vokabel gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class learnVocabularyEntry(AbstractRequestHandler): #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("LearnVocabulary")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = data.LEARNVOCENTRYHELPER
        questionsForLearnModule = dbGerToEng.getDocument()
        print(len(questionsForLearnModule))
        if not questionsForLearnModule: # check if the question list is empty | if user want lern without any entrys
            speech_text = data.LEARNVOCENTRYIFDBISEMPTY
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Vokabeln lernen fehlgeschlagen", data.WELCOME)).set_should_end_session(
                False)
            return handler_input.response_builder.response

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class questionCountRequest(AbstractRequestHandler): #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("countRequestForVocabularyLearn")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        questionsForLearnModule = dbGerToEng.getDocument()
        slots = handler_input.request_envelope.request.intent.slots
        questionCount = slots["anzahl"].value
        word = "test"

        #TODO Wenn die questionForLearnModule leer ist muss learnmoodestatus="inactiv"
        learnModeStatus = "active" # make the global status active to access the learn path in germanWordHandler or
                                   # englishWordHandler

        if int(questionCount) > len(questionsForLearnModule):
            print(len(questionsForLearnModule))
            handler_input.response_builder.speak(data.COUNTFAILURE.format(anzahl=len(questionsForLearnModule))).set_card(
                SimpleCard("Duba - Vokabeln schnell und einfach lernen", data.COUNTFAILURE.format(anzahl=len(questionsForLearnModule)))).set_should_end_session(
                False)

            return handler_input.response_builder.response

        randomVariable = random.randint(0, len(questionsForLearnModule) - 1)

        # Hier muss aus der Liste eins rausgenommen werden und in die active Questionlist eingetragen werden
        activeQuestion.append(questionsForLearnModule.pop(randomVariable))

        print(activeQuestion[0]["deutsch"])

        speech_text = data.QUESTIONMSGGERTOENG.format(vokabel=activeQuestion[0]["deutsch"])

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response

class germanWordHandler(AbstractRequestHandler): #
    """Handler for Skill Launch."""
    #TODO einzelne Wörter werden hier aufgerufen. Wir müssen einen globalen rekursiv Wert implementieren
    #TODO und wenn die Zahl != 0 -> kann diese Funktion aufgerufen werden, ansonsten return response das der Nutzer seine Eingabe richtig machen soll
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("deutschwoerter")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        word = slots["germanword"].value
        speech_text = "Deutsches Wort wurde erkannt."

        if learnModeStatus == "inactive": # this global variable manages if we want add question or learn question
            speech_text = data.BREAKFORLEARNINACTIVE
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
                False)

            return handler_input.response_builder.response

        if learnModeStatus == "active":
            return
            # TODO abgleichen des gefragten wortes und der erhaltenen antwort vom nutzer, gefragtes Wort mit session_attributes erhältlich?


        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response

class englishWordHandler(AbstractRequestHandler): #
    """Handler for Skill Launch."""
    #TODO einzelne Wörter werden hier aufgerufen. Wir müssen einen globalen Wert implementieren
    #TODO und wenn die Zahl != 0 -> kann diese Funktion aufgerufen werden, ansonsten return response das der Nutzer seine Eingabe richtig machen soll
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("englischwoerter")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        word = slots["englishword"].value


        speech_text = "Englisch Wort wurde erkannt."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response

class germanToEnglishHandler(AbstractRequestHandler): #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("germanToEnglish")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response


        speech_text = "Englisch Wort wurde erkannt."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response

class englishToGermanWordHandler(AbstractRequestHandler): #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("englishToGerman")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response


        speech_text = "Englisch Wort wurde erkannt."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Hello Python World from Classes!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can say hello to me!"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Hello World skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # any cleanup logic goes here
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        app.logger.error(exception, exc_info=True)

        speech = "Sorry, es ist ein Fehler aufgetaucht. Bitte versuchen Sie es erneut!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StoreVocabularyRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(AddVocabularyRequestHandler())
sb.add_request_handler(learnVocabularyEntry())
sb.add_request_handler(questionCountRequest())
sb.add_request_handler(germanWordHandler())
sb.add_request_handler(englishWordHandler())
sb.add_request_handler(englishToGermanWordHandler())
sb.add_request_handler(germanToEnglishHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)


@app.route('/', methods=['GET', 'POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run()
