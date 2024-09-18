import spacy
from config import SPACY_MODEL, CRISIS_INDICATORS

nlp = spacy.load(SPACY_MODEL)

def detect_crisis(user_message: str) -> bool:
    doc = nlp(user_message.lower())
    return any(indicator in doc.text for indicator in CRISIS_INDICATORS)

def get_crisis_response() -> str:
    return "I'm really concerned about what you're saying. Please reach out to a crisis helpline immediately. In the US, you can call 1-800-273-8255 or text HOME to 741741."
