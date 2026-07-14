from textblob import TextBlob

def grammar_correct(text):
    return str(TextBlob(text).correct())