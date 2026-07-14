def add_basic_punctuation(text):
    if not text:
        return text

    text = text.capitalize()

    if text[-1] not in ".!?":
        text += "."

    return text


def split_sentences(text):
    text = text.replace(" and", ".And")
    text = text.replace(" but", ".But")
    return text


def remove_repetition(text):
    words = text.split()
    cleaned = []
    for w in words:
        if not cleaned or w != cleaned[-1]:
            cleaned.append(w)
    return " ".join(cleaned)