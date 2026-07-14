from deep_translator import GoogleTranslator

languages = {
    "en": "english",
    "ta": "tamil",
    "hi": "hindi",
    "te": "telugu",
    "ko": "korean",
    "ja": "japanese"
}

def translate_text(text, target):
    try:
        return GoogleTranslator(source='auto', target=target).translate(text)
    except:
        return text