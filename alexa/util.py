from googletrans import Translator
import duden

def dudenCheck(name):
    checkWord = duden.get(name)

    if checkWord is None:
        checkWord = duden.get(name.capitalize())

    if checkWord is None:
        checkWord = duden.search(name) #TODO json picker schauen und dort erste eintrag rausnehmen
    if checkWord is None:
        checkWord = duden.search(name.capitalize())

    # try:
    #    checkWord = duden.get(name)

    # except ConnectionError as f:
    #     print(f)

    # if checkWord is None:
    #     checkWord = duden.get(name.capitalize())
    return checkWord


def translate(name):
    translator = Translator()
    translatedWord = translator.translate(text=name, dest='en', src='de').text
    return translatedWord