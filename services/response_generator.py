from typing import List, Dict, Any
import google.generativeai as genai
from config import GEMINI_MODEL

def configure_genai(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)

def generate_response(user_input: str, conversation_history: List[Dict[str, str]], context: Dict[str, Any], api_key: str) -> str:
    model = configure_genai(api_key)
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    current_mood = context.get('current_mood', {"emoji": "😐", "value": 3})
    
    prompt = f"""You are a mental health support chatbot. Provide a compassionate and helpful response to the user's input. 
    Here's the conversation history:
    {formatted_history}
    
    User's latest message: {user_input}
    
    User's current mood: {current_mood['emoji']} (Scale 1-5: {current_mood['value']})
    
    Context: {context}
    
    Based on the user's current mood, tailor your response to be more supportive or encouraging as needed. If the mood is low (1-2), offer specific coping strategies or words of encouragement. If the mood is high (4-5), reinforce positive behaviors and emotions.
    
    Respond as the chatbot:"""

    response = model.generate_content(prompt)
    return response.text
