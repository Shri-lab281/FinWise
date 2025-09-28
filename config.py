import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash"   # change to gemini-2.0-flash if you prefer speed

def get_model():
    """Return a Gemini model object"""
    return genai.GenerativeModel(MODEL_NAME)

def get_gemini_response(prompt: str,  max_output_tokens: int = 400):
    """Get response from Gemini"""
    try:
        model = get_model()
        resp = model.generate_content(prompt)
        return getattr(resp, "text", str(resp))
    except Exception as e:
        return f"Error: {e}"
