import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict

def load_country_resources() -> pd.DataFrame:
    return pd.DataFrame({
        'Country': ['India', 'United States', 'United Kingdom', 'Australia', 'Canada'],
        'Helpline': ['91-9820466726', '1-800-273-8255', '116 123', '13 11 14', '1-833-456-4566'],
        'Website': ['http://www.aasra.info/', 'https://suicidepreventionlifeline.org', 'https://www.samaritans.org', 'https://www.lifeline.org.au', 'https://www.crisisservicescanada.ca']
    })

def save_conversation(conversation: List[Dict[str, str]]) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.txt"
    with open(filename, 'w') as f:
        for entry in conversation:
            f.write(f"{entry['role']}: {entry['content']}\n")
    return filename

def get_api_key():
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    if not api_key:
        st.warning("Please enter a valid API key to use the chatbot.")
    return api_key
