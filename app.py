import streamlit as st
import random
from datetime import datetime
import spacy
import google.generativeai as genai
from streamlit_chat import message
import pandas as pd

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set up Gemini API
GOOGLE_API_KEY = "AIzaSyAwb8w2ye2P3QSkzFrnADHmnRmx16UTOhk"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class DialogManager:
    def __init__(self):
        self.context = {}

    def update_context(self, user_id, key, value):
        if user_id not in self.context:
            self.context[user_id] = {}
        self.context[user_id][key] = value

    def get_context(self, user_id):
        return self.context.get(user_id, {})

def analyze_intent(user_message):
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

def detect_crisis(user_message):
    crisis_indicators = [
        "suicide", "kill myself", "want to die", "end my life",
        "no reason to live", "better off dead", "can't go on"
    ]
    doc = nlp(user_message.lower())
    return any(indicator in doc.text for indicator in crisis_indicators)

def get_crisis_response():
    return "I'm really concerned about what you're saying. Please reach out to a crisis helpline immediately. In the US, you can call 1-800-273-8255 or text HOME to 741741."

def generate_response(user_input, conversation_history, context=None):
    formatted_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    
    current_mood = st.session_state.get('current_mood', {"emoji": "😐", "value": 3})
    
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

def save_conversation(conversation):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    with open(filename, 'w') as f:
        for entry in conversation:
            f.write(f"{entry['role']}: {entry['content']}\n")
    st.success(f"Conversation saved as {filename}")

def get_user_name():
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    user_input = st.text_input("What's your name?", value=st.session_state.user_name)
    if user_input:
        st.session_state.user_name = user_input
    
    return st.session_state.user_name

def personalized_greeting(name):
    if name:
        return f"Hello, {name}! How are you feeling today?"
    

def track_mood():
    if 'previous_mood' not in st.session_state:
        st.session_state.previous_mood = {"emoji": "😐", "value": 3}

    mood_options = {
        "😢": 1, "😕": 2, "😐": 3, "🙂": 4, "😄": 5
    }
    selected_emoji = st.select_slider(
        "How are you feeling right now?",
        options=list(mood_options.keys()),
        value=st.session_state.previous_mood["emoji"]
    )
    mood_value = mood_options[selected_emoji]
    current_mood = {"emoji": selected_emoji, "value": mood_value}
    
    mood_changed = current_mood != st.session_state.previous_mood
    st.session_state.previous_mood = current_mood
    st.session_state.current_mood = current_mood
    
    return mood_changed, current_mood

def load_country_resources():
    return pd.DataFrame({
        'Country': ['India', 'United States', 'United Kingdom', 'Australia', 'Canada'],
        'Helpline': ['91-9820466726', '1-800-273-8255', '116 123', '13 11 14', '1-833-456-4566'],
        'Website': ['http://www.aasra.info/', 'https://suicidepreventionlifeline.org', 'https://www.samaritans.org', 'https://www.lifeline.org.au', 'https://www.crisisservicescanada.ca']
    })

def get_contextual_prompt(intent):
    prompts = {
        "emotional_support": "It sounds like you're going through a tough time. Can you tell me more about what's been bothering you?",
        "anxiety_support": "I understand you're feeling anxious. What specific situations or thoughts are triggering your anxiety?",
        "self_esteem": "It's important to remember your worth. Can you share some of your recent accomplishments or positive qualities?",
        "relationship_issues": "Relationships can be challenging. What aspects of your relationships are you finding most difficult right now?",
        "general_support": "How can I support you today? Is there anything specific you'd like to talk about?"
    }
    return prompts.get(intent, prompts["general_support"])

def main():
    st.set_page_config(page_title="Mental Health Chatbot", page_icon="🤖")
    st.title("Mental Health Support Chatbot")

    user_name = get_user_name()
    if user_name:
        st.write(personalized_greeting(user_name))
    else:
        st.write("Hello! How are you feeling today?")

    mood_changed, current_mood = track_mood()
    
    if mood_changed:
        mood_responses = {
            1: "I'm sorry to hear you're feeling down. Remember, it's okay to have tough days. Would you like to talk about what's bothering you?",
            2: "It seems like you're having a bit of a rough time. Is there anything specific on your mind that you'd like to discuss?",
            3: "I see you're feeling neutral today. How about we explore ways to boost your mood a little?",
            4: "It's great to see you're in a good mood! What positive things have been happening in your life recently?",
            5: "Wonderful! You're feeling great today. Let's talk about how to maintain this positive energy!"
        }
        
        st.write(mood_responses[current_mood['value']])

    # Initialize session states
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(random.randint(1000, 9999))
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    # Display chat messages
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    dialog_manager = DialogManager()

    # Load country resources
    country_resources = load_country_resources()

    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.spinner("Thinking..."):
            intent = analyze_intent(prompt)
            dialog_manager.update_context(st.session_state.session_id, "intent", intent)

            if detect_crisis(prompt):
                response = get_crisis_response()
            else:
                context = dialog_manager.get_context(st.session_state.session_id)
                response = generate_response(prompt, st.session_state.messages, context)

        st.chat_message("assistant").markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        contextual_prompt = get_contextual_prompt(intent)
        st.text_input("Chatbot suggests:", value=contextual_prompt, key="contextual_prompt", disabled=True)

    if st.button("Save Conversation"):
        save_conversation(st.session_state.messages)

    # Sidebar content
    st.sidebar.header("Resources")
    
    # Country selector
    selected_country = st.sidebar.selectbox("Select your country", country_resources['Country'].tolist())
    
    # Display country-specific resources
    if selected_country:
        country_data = country_resources[country_resources['Country'] == selected_country].iloc[0]
        st.sidebar.markdown(f"**Helpline:** {country_data['Helpline']}")
        st.sidebar.markdown(f"**Website:** [{selected_country} Mental Health Support]({country_data['Website']})")

    # Add disclaimer to sidebar using markdown
    st.sidebar.success(
        "### Disclaimer\n"
        "This chatbot is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. "
        "Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition."
    )

if __name__ == "__main__":
    main()
