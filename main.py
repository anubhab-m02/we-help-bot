import streamlit as st
import random
from config import MOOD_OPTIONS
from utils.nlp_utils import analyze_intent, get_contextual_prompt
from utils.data_utils import load_country_resources, save_conversation, get_api_key
from models.dialog_manager import DialogManager
from services.crisis_detector import detect_crisis, get_crisis_response
from services.response_generator import generate_response

# Remove the following imports as they're now handled in separate modules:
# import spacy
# import google.generativeai as genai
# from streamlit_chat import message
# import pandas as pd
# from datetime import datetime

def get_user_name() -> str:
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    
    user_input = st.text_input("What's your name?", value=st.session_state.user_name)
    if user_input:
        st.session_state.user_name = user_input
    
    return st.session_state.user_name

def personalized_greeting(name: str) -> str:
    return f"Hello, {name}! How are you feeling today?" if name else "Hello! How are you feeling today?"

def track_mood() -> tuple:
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
    
    return mood_changed, current_mood

def main():
    st.set_page_config(page_title="Mental Health Chatbot", page_icon="🤖")
    st.title("Mental Health Support Chatbot")

    api_key = get_api_key()
    if not api_key:
        return

    user_name = get_user_name()
    st.write(personalized_greeting(user_name))

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

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.spinner("Thinking..."):
            intent = analyze_intent(prompt)
            dialog_manager.update_context(st.session_state.session_id, "intent", intent)

            if detect_crisis(prompt):
                response = get_crisis_response()
            else:
                context = dialog_manager.get_context(st.session_state.session_id)
                context['current_mood'] = current_mood
                response = generate_response(prompt, st.session_state.messages, context, api_key)

        st.chat_message("assistant").markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        contextual_prompt = get_contextual_prompt(intent)
        st.text_input("Chatbot suggests:", value=contextual_prompt, key="contextual_prompt", disabled=True)

    if st.button("Save Conversation"):
        filename = save_conversation(st.session_state.messages)
        st.success(f"Conversation saved as {filename}")

    # Sidebar content
    with st.sidebar:
        st.header("Mental Health Resources")
        country_resources = load_country_resources()
        selected_country = st.selectbox("Select your country:", country_resources['Country'].tolist())
        
        if selected_country:
            resource = country_resources[country_resources['Country'] == selected_country].iloc[0]
            st.write(f"Helpline: {resource['Helpline']}")
            st.write(f"Website: {resource['Website']}")
        # Add disclaimer to sidebar using markdown
    st.sidebar.success(
        "### Disclaimer\n"
        "This chatbot is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. "
        "Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition."
    )

if __name__ == "__main__":
    main()