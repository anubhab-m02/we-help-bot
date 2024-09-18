import spacy
from config import SPACY_MODEL

nlp = spacy.load(SPACY_MODEL)

def analyze_intent(user_message: str) -> str:
    doc = nlp(user_message)
    intent_keywords = {
        "emotional_support": ["sad", "depressed", "unhappy", "lonely"],
        "anxiety_support": ["anxious", "worried", "stress", "panic"],
        "self_esteem": ["worthless", "hate myself", "not good enough"],
        "relationship_issues": ["breakup", "divorce", "fight", "argument"],
        "general_support": []  # Default category
    }
    
    for intent, keywords in intent_keywords.items():
        if any(token.lemma_.lower() in keywords for token in doc):
            return intent
    
    return "general_support"

def get_contextual_prompt(intent: str) -> str:
    prompts = {
        "emotional_support": "It sounds like you're going through a tough time. Can you tell me more about what's been bothering you?",
        "anxiety_support": "I understand you're feeling anxious. What specific situations or thoughts are triggering your anxiety?",
        "self_esteem": "It's important to remember your worth. Can you share some of your recent accomplishments or positive qualities?",
        "relationship_issues": "Relationships can be challenging. What aspects of your relationships are you finding most difficult right now?",
        "general_support": "How can I support you today? Is there anything specific you'd like to talk about?"
    }
    return prompts.get(intent, prompts["general_support"])
