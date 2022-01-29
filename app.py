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
values = util.ChangeableVariables(False)

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

        values.setMenuState(False)

        speech_text = data.ADDQUESTLANGUAGEREQUESTMSG

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Vokabel hinzufügen", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class EnglishStoreVocabularyRequestHandler(AbstractRequestHandler):
    """Handler for option to add vocabulary"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("englischwoerter")(handler_input) and (values.getMenuState() == False))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        val = slots["englishword"].value

        translation = util.translate(val, 'de', 'en')
        print(translation)

        try:
            dbEngToGer = db.DatabaseManager(random.randint(1000, 9999), val.lower(), translation.lower(), False)
            dbEngToGer.createInstanceEngToGer()
            questionsForLearnModule = dbEngToGer.getGermanDocument()
        except Exception as e:
            print(e)

        speech_text = data.STOREVOCABULARYSPEECHTEXT.format(checkword=val, transl=translation)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Vokabel gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class GermanStoreVocabularyRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StoreVocabulary")(handler_input) or \
               (is_intent_name("deutschwoerter")(handler_input) and (values.getMenuState() == False))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots

        try:
            val = slots["germanword"].value
        except Exception as e:
            print(e)

        if not val:
            try:
                val = slots["wordForTranslation"].value
            except Exception as e:
                print(e)

        checkVoc = util.dudenCheck(val)
        print(checkVoc.name)

        translation = util.translate(val, 'en', 'de')
        print(translation)

        try:
            dbGerToEng = db.DatabaseManager(random.randint(1000, 9999), checkVoc.name.lower(), translation.lower(), False)
            dbGerToEng.createInstanceGerToEng()
            questionsForLearnModule = dbGerToEng.getGermanDocument()
        except Exception as e:
            print(e)

        speech_text = data.STOREVOCABULARYSPEECHTEXT.format(checkword=checkVoc.name, transl=translation)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Vokabel gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class LearnVocabularyEntry(AbstractRequestHandler):  #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("LearnVocabulary")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = data.LEARNVOCENTRYHELPER
        values.setMenuState(True)
        questionsForLearnModule = db.DatabaseManager().getGermanDocument()
        print(len(values.getGermanQuestionForLearn()))
        if not questionsForLearnModule:  # check if the question list is empty | if user want learn without any entrys
            speech_text = data.LEARNVOCENTRYIFDBISEMPTY
            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Vokabeln lernen fehlgeschlagen", data.WELCOME)).set_should_end_session(
                False)
            return handler_input.response_builder.response

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class QuestionCountRequest(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("countRequestForVocabularyLearn")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        questionCount = slots["anzahl"].value
        values.setQuestionCount(int(questionCount))
        learnDirection = values.getLearnDirection()

        print(learnDirection)

        if learnDirection == "germanToEnglish":
            dbEntryCount = len(values.getGermanQuestionForLearn())
        if learnDirection == "englishToGerman":
            dbEntryCount = len(values.getEnglishQuestionForLearn())

        print(dbEntryCount)
        if int(questionCount) > dbEntryCount:
            print(dbEntryCount)
            handler_input.response_builder.speak(data.COUNTFAILURE.format(anzahl=dbEntryCount)).set_card(
                SimpleCard("Duba - Vokabeln schnell und einfach lernen",
                           data.COUNTFAILURE.format(anzahl=dbEntryCount))).set_should_end_session(
                False)

            return handler_input.response_builder.response

        randomVariable = random.randint(0, dbEntryCount - 1)

        values.setActiveQuestion(randomVariable)

        print(values.getActiveQuestion()[0]["deutsch"])
        print(values.getActiveQuestion()[0]["englisch"])

        if learnDirection == "germanToEnglish":
            speech_text = data.QUESTIONMSGGERTOENG.format(vokabel=values.getActiveQuestion()[0]["deutsch"])
        if learnDirection == "englishToGerman":
            speech_text = data.QUESTIONMSGENGTOGER.format(vokabel=values.getActiveQuestion()[0]["englisch"])

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class GermanWordHandler(AbstractRequestHandler):  #
    """Handler for handling german words"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("deutschwoerter")(handler_input) and (values.getMenuState() == True)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        word = slots["germanword"].value
        questionCount = values.getQuestionCount()

        if word == values.getActiveQuestion()[0]["deutsch"]:
            if questionCount <= 1:  # if the count reaches 0, the learning is done
                values.clearEntrys()
                speech_text = data.LEARNSUCCESSFULLYEND

                handler_input.response_builder.speak(speech_text).set_card(
                    SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
                    False)

                return handler_input.response_builder.response

            values.setQuestionCount(questionCount - 1)  # Count of question will be reduced by 1
            dbEntryCount = len(values.getEnglishQuestionForLearn())
            randomVariable = random.randint(0, dbEntryCount - 1)
            values.setActiveQuestion(randomVariable)

            speech_text = data.QUESTIONSUCCESSFORENGLISHWORDS.format(count=values.getQuestionCount(), englishWord=values.getActiveQuestion()[0]["englisch"])

            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
                False)

            return handler_input.response_builder.response

        speech_text = data.RETRYENGLISHWORDONFAILURE.format(germanWord=values.getActiveQuestion()[0]["deutsch"])

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class EnglishWordHandler(AbstractRequestHandler):  #
    """Handler for handle english words."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("englischwoerter")(handler_input) and (values.getMenuState() == True)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        word = slots["englishword"].value
        counter = values.getQuestionCount()

        if word == values.getActiveQuestion()[0]["englisch"]:

            if counter <= 1:  # if the count reaches 0, the learning is done
                values.clearEntrys()
                speech_text = data.LEARNSUCCESSFULLYEND

                handler_input.response_builder.speak(speech_text).set_card(
                    SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
                    False)

                return handler_input.response_builder.response

            values.setQuestionCount(counter - 1)  # Count of question will be reduced by 1
            dbEntryCount = len(values.getGermanQuestionForLearn())
            randomVariable = random.randint(0, dbEntryCount - 1)
            values.setActiveQuestion(randomVariable)

            speech_text = data.QUESTIONSUCCESSFORGERMANWORDS.format(count=values.getQuestionCount(), germanWord=values.getActiveQuestion()[0]["deutsch"])

            handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
                False)

            return handler_input.response_builder.response

        speech_text = data.RETRYGERMANWORDONFAILURE.format(englishWord=values.getActiveQuestion()[0]["englisch"])


        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response



class LearnGermanToEnglishHandler(AbstractRequestHandler):  #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("germanToEnglish")(handler_input) and (values.getMenuState() == True))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        values.setLearnDirection("germanToEnglish")

        speech_text = data.LEARNVOCABULARYCOUNTMSG

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class LearnEnglishToGermanWordHandler(AbstractRequestHandler):  #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("englishToGerman")(handler_input) and (values.getMenuState() == True))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        values.setLearnDirection("englishToGerman")

        speech_text = data.LEARNVOCABULARYCOUNTMSG

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class AddGermanToEnglishHandler(AbstractRequestHandler):  #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("germanToEnglish")(handler_input) and (values.getMenuState() == False))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = data.ADDVOCABULARYHELPER

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Duba - Vokabeln schnell und einfach lernen", speech_text)).set_should_end_session(
            False)

        return handler_input.response_builder.response


class AddEnglishToGermanWordHandler(AbstractRequestHandler):  #
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("englishToGerman")(handler_input) and (values.getMenuState() == False))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = data.ADDVOCABULARYENGHELPER

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
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(AddVocabularyRequestHandler())
sb.add_request_handler(LearnVocabularyEntry())
sb.add_request_handler(QuestionCountRequest())
sb.add_request_handler(GermanWordHandler())
sb.add_request_handler(EnglishWordHandler())
sb.add_request_handler(LearnEnglishToGermanWordHandler())
sb.add_request_handler(LearnGermanToEnglishHandler())
sb.add_request_handler(AddEnglishToGermanWordHandler())
sb.add_request_handler(AddGermanToEnglishHandler())
sb.add_request_handler(GermanStoreVocabularyRequestHandler())
sb.add_request_handler(EnglishStoreVocabularyRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)


@app.route('/', methods=['GET', 'POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()


if __name__ == '__main__':
    app.run()
